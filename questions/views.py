from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import Question, Answer, Tag, User
from django.contrib.auth import logout as _logout

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

def question(request, question_id):
    question_item = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'), 
        pk=question_id
    )
    answers = Answer.objects.filter(question=question_item)\
        .select_related('author')\
        .order_by('-created_at')
    page, page_range = paginate(answers, request, per_page=5)
    context = {
        'question': question_item, 
        'answers': page, 
        'page_range': page_range
    }
    context.update(get_global_context(request))
    return render(request, 'pages/question.html', context)

def login(request):
    context = get_global_context(request)
    return render(request, 'pages/login.html', context)

def signup(request):
    context = get_global_context(request)
    return render(request, 'pages/signup.html', context)

def ask(request):
    context = get_global_context(request)
    return render(request, 'pages/ask.html', context)
    
def settings(request):
    context = get_global_context(request)
    return render(request, 'pages/settings.html', context)

def logout(request):
    _logout(request)
    return redirect('index')
