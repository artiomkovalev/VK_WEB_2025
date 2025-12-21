from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Count, Sum
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.http import JsonResponse
from questions.services import toggle_vote
from .models import Question, Answer, Tag, User, QuestionLike, AnswerLike
from .forms import LoginForm, RegistrationForm, SettingsForm, QuestionForm, AnswerForm

QUESTIONS_PER_PAGE = 10
ANSWERS_PER_PAGE = 5

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    text_range = []
    active_pages = {1, paginator.num_pages, page.number, page.number - 1, page.number + 1}
    pages = sorted(list(page for page in active_pages if 0 < page <= paginator.num_pages))
    prev = 0
    for p in pages:
        if prev > 0:
            if p - prev == 2:
                text_range.append(prev + 1)
            elif p - prev > 2:
                text_range.append('...')
        text_range.append(p)
        prev = p
    return page, text_range

class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_tags'] = Tag.objects.popular()
        context['best_members'] = User.objects.best()
        return context

class BaseQuestionListView(SidebarMixin, ListView):
    model = Question
    template_name = 'pages/index.html'
    context_object_name = 'page'
    paginate_by = QUESTIONS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.object_list 
        page, page_range = paginate(queryset, self.request, self.paginate_by)
        context['page'] = page
        context['page_range'] = page_range
        return context

class IndexView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.new()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New questions'
        return context

class HotView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.hot()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Hot questions'
        return context

class TagView(BaseQuestionListView):
    def get_queryset(self):
        self.tag_obj = get_object_or_404(Tag, name=self.kwargs['tag_name'])
        return Question.objects.filter(tags=self.tag_obj)\
            .select_related('author')\
            .prefetch_related('tags')\
            .annotate(num_answers=Count('answer'))\
            .order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_name'] = self.kwargs['tag_name']
        return context

class QuestionDetailView(SidebarMixin, DetailView):
    model = Question
    template_name = 'pages/question.html'
    pk_url_kwarg = 'question_id'
    context_object_name = 'question'

    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answers = self.object.answer_set.select_related('author').order_by('created_at')
        
        page, page_range = paginate(answers, self.request, per_page=ANSWERS_PER_PAGE)
        
        context['answers'] = page
        context['page_range'] = page_range
        context['form'] = AnswerForm()
        return context

class AddAnswerView(LoginRequiredMixin, SidebarMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'pages/question.html'

    def form_valid(self, form):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        answer = form.save(user=self.request.user, question=question)
        total_answers = question.answer_set.count()
        page_num = (total_answers // ANSWERS_PER_PAGE) + 1 if total_answers % ANSWERS_PER_PAGE != 0 else (total_answers // ANSWERS_PER_PAGE)
        return redirect(f"{question.get_absolute_url()}?page={page_num}#answer-{answer.id}")

    def form_invalid(self, form):
        question = get_object_or_404(
            Question.objects.select_related('author').prefetch_related('tags'), 
            pk=self.kwargs['question_id']
        )
        answers = question.answer_set.select_related('author').order_by('created_at')
        page, page_range = paginate(answers, self.request, per_page=ANSWERS_PER_PAGE)
        context = self.get_context_data(
            question=question,
            answers=page,
            page_range=page_range,
            form=form
        )
        return render(self.request, self.template_name, context)

class AskView(LoginRequiredMixin, SidebarMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'pages/ask.html'

    def form_valid(self, form):
        question = form.save(user=self.request.user)
        return redirect(question)

class SettingsView(LoginRequiredMixin, SidebarMixin, UpdateView):
    model = User
    form_class = SettingsForm
    template_name = 'pages/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user

class UserSignupView(SidebarMixin, CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'pages/signup.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        auth_login(self.request, self.object)
        return response

class UserLoginView(SidebarMixin, LoginView):
    template_name = 'pages/login.html'
    form_class = LoginForm
    
    def get_success_url(self):
        url = self.request.POST.get('next') or self.request.GET.get('next')
        return url or super().get_success_url()

class UserLogoutView(LogoutView):
    def get_next_page(self):
        return self.request.GET.get('next') or reverse('index')

class BaseVoteView(LoginRequiredMixin, View):
    model = None
    like_model = None
    related_field_name = None

    def handle_no_permission(self):
        return JsonResponse({'error': 'Log in to vote'}, status=401)

    def post(self, request, question_id):
        vote_type = request.POST.get('vote_type')
        vote_value = 1 if vote_type == 'up' else -1
        obj = get_object_or_404(self.model, pk=question_id)
        try:
            new_rating = toggle_vote(
                user=request.user,
                obj=obj,
                like_model_class=self.like_model,
                related_field_name=self.related_field_name,
                vote_value=vote_value
            )
            return JsonResponse({'rating': new_rating})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=403)
        except Exception as e:
            return JsonResponse({'error': 'Something went wrong'}, status=500)

class QuestionVoteView(BaseVoteView):
    model = Question
    like_model = QuestionLike
    related_field_name = 'question'

class AnswerVoteView(BaseVoteView):
    model = Answer
    like_model = AnswerLike
    related_field_name = 'answer'

class MarkCorrectView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please log in'}, status=401)
        
        if request.method.lower() != 'post':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        answer_id = request.POST.get('answer_id')

        try:
            self.answer = Answer.objects.select_related('question').get(pk=answer_id)
        except Answer.DoesNotExist:
            return JsonResponse({'error': 'Answer not found'}, status=404)
        
        if request.user != self.answer.question.author:
            return JsonResponse({'error': 'You are not the author'}, status=403)
    
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                question = self.answer.question
                
                if self.answer.is_correct:
                    self.answer.is_correct = False
                    self.answer.save(update_fields=['is_correct'])
                else:
                    question.answer_set.exclude(pk=self.answer.pk).update(is_correct=False)
                    self.answer.is_correct = True
                    self.answer.save(update_fields=['is_correct'])
            return JsonResponse({'status': self.answer.is_correct})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class SearchSuggestionsView(View):

    def get(self, request):
        query = request.GET.get('q', '')

        if len(query) < 2:
            return JsonResponse({'results': []})

        vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
        search_query = SearchQuery(query)

        questions = Question.objects.annotate(
            rank=SearchRank(vector, search_query)
        ).filter(rank__gte=0.1).order_by('-rank')[:5]

        results = [
            {
                'id': q.id,
                'title': q.title,
                'url': q.get_absolute_url()
            } for q in questions
        ]
        
        return JsonResponse({'results': results})
