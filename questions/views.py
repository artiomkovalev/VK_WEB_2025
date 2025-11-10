from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

QUESTIONS = [
  {
    'id': i,
    'title': f'Question #{i}',
    'text': f'Text of question #{i}.',
    'tags': ['python', 'django', 'web'],
    'rating': i,
  } for i in range(30)
]

ANSWERS = [
  {
      'id': i,
      'text': f'Answer #{i}.',
      'rating': i,
  } for i in range(100)
]

HOT_QUESTIONS = sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)

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
  page = paginate(QUESTIONS, request)
  context = {
    'page': page,
    'title': 'New Questions',
    'hot_questions': HOT_QUESTIONS[:5]
  }
  return render(request, 'index.html', context)

def hot(request):
  page = paginate(HOT_QUESTIONS, request)
  context = {
    'page': page,
    'title': 'Hot Questions',
    'hot_questions': HOT_QUESTIONS[:5]
  }
  return render(request, 'index.html', context)

def tag(request, tag_name):
  questions_by_tag = [q for q in QUESTIONS if tag_name in q['tags']]
  page = paginate(questions_by_tag, request)
  context = {
    'page': page,
    'tag_name': tag_name,
    'hot_questions': HOT_QUESTIONS[:5]
  }
  return render(request, 'index.html', context)

def question(request, question_id):
  try:
    question_item = QUESTIONS[question_id]
  except IndexError:
    return render(request, '404.html')
  page = paginate(ANSWERS, request, per_page=3)
  context = {
      'question': question_item,
      'answers': page,
      'hot_questions': HOT_QUESTIONS[:5]
  }
  return render(request, 'question.html', context)

def login(request):
  return render(request, 'login.html')

def signup(request):
  return render(request, 'signup.html')

def ask(request):
  return render(request, 'ask.html')

def settings(request):
  return render(request, 'settings.html')
