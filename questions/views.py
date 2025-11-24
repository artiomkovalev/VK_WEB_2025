from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import Question, Answer, Tag, User
from .forms import LoginForm, RegistrationForm, SettingsForm, QuestionForm, AnswerForm
from django.urls import reverse
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

def get_global_context(request):
    return {
        'popular_tags': Tag.objects.popular(),
        'best_members': User.objects.best(),
    }

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

def index(request):
    questions = Question.objects.new()
    page, page_range = paginate(questions, request, per_page=10)
    context = {
        'page': page, 
        'title': 'New Questions', 
        'page_range': page_range
    }
    context.update(get_global_context(request))
    return render(request, 'pages/index.html', context)

def hot(request):
    questions = Question.objects.hot()
    page, page_range = paginate(questions, request, per_page=10)
    context = {
        'page': page, 
        'title': 'Hot Questions', 
        'page_range': page_range
    }
    context.update(get_global_context(request))
    return render(request, 'pages/index.html', context)

def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.filter(tags=tag_obj)\
        .select_related('author')\
        .prefetch_related('tags')\
        .annotate(num_answers=Count('answer'))\
        .order_by('-created_at')
    page, page_range = paginate(questions, request, per_page=10)
    context = {
        'page': page, 
        'tag_name': tag_name, 
        'page_range': page_range
    }
    context.update(get_global_context(request))
    return render(request, 'pages/index.html', context)

@require_http_methods(['GET', 'POST'])
def question(request, question_id):
    question_item = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'), 
        pk=question_id
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question_item
            answer.save()
            total_answers = question_item.answer_set.count()
            page_num = (total_answers // 5) + 1 if total_answers % 5 != 0 else (total_answers // 5)
            return redirect(f"{question_item.get_absolute_url()}?page={page_num}#answer-{answer.id}")
    else:
        form = AnswerForm()

    answers = Answer.objects.filter(question=question_item).select_related('author').order_by('created_at')
    
    page, page_range = paginate(answers, request, per_page=5)
    
    context = {
        'question': question_item, 
        'answers': page, 
        'page_range': page_range,
        'form': form
    }
    context.update(get_global_context(request))
    return render(request, 'pages/question.html', context)

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                _login(request, user)
                redirect_url = request.POST.get('continue') or request.GET.get('continue') or 'index'
                return redirect(redirect_url)
            else:
                form.add_error(None, 'Invalid login or password')
    else:
        form = LoginForm()

    context = {'form': form}
    context.update(get_global_context(request))
    return render(request, 'pages/login.html', context)

@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            _login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()
        
    context = {'form': form}
    context.update(get_global_context(request))
    return render(request, 'pages/signup.html', context)

@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            tag_names = form.cleaned_data['tags']
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)
            
            return redirect(question)
    else:
        form = QuestionForm()

    context = {'form': form}
    context.update(get_global_context(request))
    return render(request, 'pages/ask.html', context)

@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('settings') 
    else:
        form = SettingsForm(instance=request.user)
    
    context = {'form': form}
    context.update(get_global_context(request))
    return render(request, 'pages/settings.html', context)

def logout(request):
    _logout(request)
    next_page = request.GET.get('next')
    if next_page:
        return redirect(next_page)
    return redirect('index')
