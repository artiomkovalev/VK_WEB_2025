from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Count

class ProfileManager(models.Manager):
    def best(self):
        return self.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, null=True)
    
    objects = ProfileManager()

    def __str__(self):
        return f"Профиль пользователя #{self.user.username}"

class TagManager(models.Manager):
    def popular(self):
        return self.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    objects = TagManager()

    def __str__(self):
        return f"#{self.name}"

class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
            .select_related('author', 'author__user')\
            .prefetch_related('tags')\
            .annotate(num_answers=Count('answer'))
    
    def new(self):
        return self.get_queryset().order_by('-created_at')

    def hot(self):
        return self.get_queryset().order_by('-rating')

class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)
  
    objects = QuestionManager()

    def __str__(self):
        return f"{self.title} (by {self.author.user.username})"

    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})

class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer to '{self.question.title}' (by {self.author.user.username})"


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])

    class Meta:
        unique_together = ('user', 'question')

class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])

    class Meta:
        unique_together = ('user', 'answer')
