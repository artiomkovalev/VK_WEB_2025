from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hot/', views.HotView.as_view(), name='hot'),
    path('tag/<str:tag_name>/', views.TagView.as_view(), name='tag'),
    path('question/<int:question_id>/', views.QuestionDetailView.as_view(), name='question'),
    path('question/<int:question_id>/answer/', views.AddAnswerView.as_view(), name='add_answer'),
    path('ask/', views.AskView.as_view(), name='ask'),
    path('profile/edit/', views.SettingsView.as_view(), name='settings'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]
