from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('question/<int:question_id>/', views.question, name='question'),
  path('ask/', views.ask, name='ask'),
  path('login/', views.login, name='login'),
  path('register/', views.signup, name='signup'),
  path('settings/', views.settings, name='settings'),
  path('tag/<str:tag_name>/', views.tag, name='tag')
]
