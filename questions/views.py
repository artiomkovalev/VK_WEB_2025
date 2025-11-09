from django.shortcuts import render

def index(request):
  context = {'title': 'New questions'}
  return render(request, 'index.html', context)

def question(request, question_id):
  return render(request, 'question.html')

def ask(request):
  return render(request, 'ask.html')

def login(request):
  return render(request, 'login.html')

def signup(request):
  return render(request, 'signup.html')

def settings(request):
  return render(request, 'settings.html')
  
def tag(request, tag_name):
  context = {'tag_name': tag_name}
  return render(request, 'index.html', context)
