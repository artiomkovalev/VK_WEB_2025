from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Question, Answer, Tag

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
    return render(request, 'index.html', {'page': page, 'title': 'New Questions', 'page_range': page_range})

def hot(request):
    questions = Question.objects.hot()
    page, page_range = paginate(questions, request, per_page=10)
    return render(request, 'index.html', {'page': page, 'title': 'Hot Questions', 'page_range': page_range})

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.filter(tags=tag).order_by('-created_at')
    page, page_range = paginate(questions, request, per_page=10)
    return render(request, 'index.html', {'page': page, 'tag_name': tag_name, 'page_range': page_range})

def question(request, question_id):
    question_item = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question_item).order_by('-created_at')
    page, page_range = paginate(answers, request, per_page=5)
    return render(request, 'question.html', {'question': question_item, 'answers': page, 'page_range': page_range})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')
    
def settings(request):
    return render(request, 'settings.html')
