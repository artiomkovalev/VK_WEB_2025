from django import forms
from django.contrib.auth import get_user_model
from .models import Question, Answer

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter login'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))

    def clean(self):
        return super().clean()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_repeat = forms.CharField(widget=forms.PasswordInput)
    upload_avatar = forms.ImageField(required=False, label="Upload avatar")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")

        if password != password_repeat:
            self.add_error('password_repeat', "Passwords do not match!")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if self.cleaned_data.get('upload_avatar'):
            user.avatar = self.cleaned_data['upload_avatar']
        if commit:
            user.save()
        return user

class SettingsForm(forms.ModelForm):
    first_name = forms.CharField(label='Nickname', required=False) 

    class Meta:
        model = User
        fields = ['email', 'first_name', 'avatar'] 

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'tag1, tag2, tag3'}))

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'How to build a moon park?'}),
            'text': forms.Textarea(attrs={'rows': 8}),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags')
        if not tags_str:
            return []

        tag_list = [t.strip() for t in tags_str.split(',') if t.strip()]
        return tag_list

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your answer here...'}),
        }
