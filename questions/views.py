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
  return page

def index(request):
  questions = Question.objects.new()
  page = paginate(questions, request, per_page=10)
  return render(request, 'index.html', {'page': page, 'title': 'New Questions'})

def hot(request):
  questions = Question.objects.hot()
  page = paginate(questions, request, per_page=10)
  return render(request, 'index.html', {'page': page, 'title': 'Hot Questions'})

def tag(request, tag_name):
  tag = get_object_or_404(Tag, name=tag_name)
  questions = Question.objects.filter(tags=tag).order_by('-created_at')
  page = paginate(questions, request, per_page=10)
  return render(request, 'index.html', {'page': page, 'tag_name': tag_name})

def question(request, question_id):
  question_item = get_object_or_404(Question, pk=question_id)
  answers = Answer.objects.filter(question=question_item).order_by('-created_at')
  page = paginate(answers, request, per_page=5)
  return render(request, 'question.html', {'question': question_item, 'answers': page})

def login(request):
  return render(request, 'login.html')

def signup(request):
  return render(request, 'signup.html')

def ask(request):
  return render(request, 'ask.html')
    
def settings(request):
  return render(request, 'settings.html')
