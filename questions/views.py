from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .models import Question, Answer, Tag, User
from .forms import LoginForm, RegistrationForm, SettingsForm, QuestionForm, AnswerForm

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
    paginate_by = 10 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        page, page_range = paginate(queryset, self.request, self.paginate_by)
        context['page'] = page
        context['page_range'] = page_range
        return context

class IndexView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.new()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Questions'
        return context

class HotView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.hot()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Hot Questions'
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
        answers = Answer.objects.filter(question=self.object)\
            .select_related('author')\
            .order_by('created_at')
        
        page, page_range = paginate(answers, self.request, per_page=5)
        
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
        answer = form.save(commit=False)
        answer.author = self.request.user
        answer.question = question
        answer.save()
        total_answers = question.answer_set.count()
        page_num = (total_answers // 5) + 1 if total_answers % 5 != 0 else (total_answers // 5)
        
        return redirect(f"{question.get_absolute_url()}?page={page_num}#answer-{answer.id}")

    def form_invalid(self, form):
        question = get_object_or_404(Question.objects.select_related('author').prefetch_related('tags'), pk=self.kwargs['question_id'])
        answers = Answer.objects.filter(question=question).select_related('author').order_by('created_at')
        page, page_range = paginate(answers, self.request, per_page=5)
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
        question = form.save(commit=False)
        question.author = self.request.user
        question.save()
        tag_names = form.cleaned_data['tags']
        if tag_names:
            Tag.objects.bulk_create(
                [Tag(name=name) for name in tag_names],
                ignore_conflicts=True
            )
            tags = Tag.objects.filter(name__in=tag_names)
            QuestionTag = Question.tags.through
            QuestionTag.objects.bulk_create([
                QuestionTag(question_id=question.id, tag_id=tag.id)
                for tag in tags
            ], ignore_conflicts=True)
            
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
