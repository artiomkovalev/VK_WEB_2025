from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Question, Answer, Tag
from .validators import validate_file_size


User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter login'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Password must be at least 8 characters long and not too common"
    )
    password_repeat = forms.CharField(widget=forms.PasswordInput)
    upload_avatar = forms.ImageField(required=False, label="Upload avatar", validators=[validate_file_size])

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        user = self.instance
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        
        if password:
            validate_password(password, user=user)
            
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")

        if password and password_repeat and password != password_repeat:
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
    email = forms.EmailField(required=True, widget=forms.EmailInput)
    first_name = forms.CharField(label='First name', required=False)
    avatar = forms.ImageField(required=False, validators=[validate_file_size])

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
        for tag in tag_list:
            if len(tag) > 50:
                raise ValidationError(
                    f'Tag "{tag}" is too long. Each tag must be 50 characters or less'
                )
        return list(set(tag_list))
    
    def save(self, user=None, commit=True):
        with transaction.atomic():
            question = super().save(commit=False)
            if user:
                question.author = user
            if commit:
                question.save()
            tag_names = self.cleaned_data['tags']
            if tag_names:
                if isinstance(tag_names, str):
                    names = [t.strip() for t in tag_names.split(',') if t.strip()]
                else:
                    names = tag_names
                if names:
                    Tag.objects.bulk_create(
                        [Tag(name=name) for name in names],
                        ignore_conflicts=True
                    )
                    tags = Tag.objects.filter(name__in=names)
                    QuestionTag = Question.tags.through
                    QuestionTag.objects.bulk_create([
                        QuestionTag(question_id=question.id, tag_id=tag.id)
                        for tag in tags
                    ], ignore_conflicts=True)
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your answer here...'}),
        }
    
    def save(self, user=None, question=None, commit=True):
        answer = super().save(commit=False)
        if user:
            answer.author = user
        if question:
            answer.question = question
        if commit:
            answer.save()
        return answer
