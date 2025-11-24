import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, OuterRef, Subquery
from django.db.models.functions import Coalesce
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike

User = get_user_model()

class Command(BaseCommand):
    help = 'Fills the database with test data based on a given ratio.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='The ratio for data generation.')
    
    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        print(f'Starting to fill database with ratio: {ratio}...')
    
        print('Creating users...')
        password_hash = make_password('password123')
        
        users = [
            User(
                username=f'{fake.word()}_{i}_{random.randint(10000, 99999)}', 
                email=f'{fake.word()}_{i}_{random.randint(10000, 99999)}@example.com',
                password=password_hash
            ) 
            for i in range(ratio)
        ]
        User.objects.bulk_create(users, batch_size=500)

        new_users_ids = list(User.objects.values_list('id', flat=True).order_by('-id')[:ratio])

        print('Creating tags...')
        tags = [Tag(name=f'{fake.word()}_{i}_{random.randint(1, 10000)}') for i in range(ratio)]
        Tag.objects.bulk_create(tags, batch_size=500, ignore_conflicts=True)
        all_tags = list(Tag.objects.all()[:ratio])

        print('Creating questions...')
        questions = []
        for i in range(ratio * 10):
            questions.append(Question(
                author_id=random.choice(new_users_ids),
                title=fake.sentence(nb_words=5),
                text=fake.paragraph(nb_sentences=3)
            ))
        Question.objects.bulk_create(questions, batch_size=500)
        new_questions = list(Question.objects.all().order_by('-id')[:ratio * 10])
        question_ids = [q.id for q in new_questions]

        print('Adding tags to questions...')
        QuestionTag = Question.tags.through
        through_objects = []
        for q in new_questions:
            if all_tags:
                chosen_tags = random.sample(all_tags, k=random.randint(1, min(4, len(all_tags))))
                for tag in chosen_tags:
                    through_objects.append(QuestionTag(question_id=q.id, tag_id=tag.id))
        
        QuestionTag.objects.bulk_create(through_objects, batch_size=10000, ignore_conflicts=True)

        print('Creating answers...')
        answers = []
        for i in range(ratio * 100):
            answers.append(Answer(
                author_id=random.choice(new_users_ids),
                question_id=random.choice(question_ids),
                text=fake.paragraph(nb_sentences=2)
            ))
        Answer.objects.bulk_create(answers, batch_size=500)
        new_answers = list(Answer.objects.all().order_by('-id')[:ratio * 100])
        answer_ids = [a.id for a in new_answers]

        print('Creating likes...')

        question_likes = []
        for _ in range(ratio * 100):
            question_likes.append(QuestionLike(
                user_id=random.choice(new_users_ids),
                question_id=random.choice(question_ids),
                value=random.choice([1, -1])
            ))
        QuestionLike.objects.bulk_create(question_likes, batch_size=5000, ignore_conflicts=True)

        print('Creating answer likes...')

        answer_likes = []
        for _ in range(ratio * 100):
            answer_likes.append(AnswerLike(
                user_id=random.choice(new_users_ids),
                answer_id=random.choice(answer_ids),
                value=random.choice([1, -1])
            ))
        AnswerLike.objects.bulk_create(answer_likes, batch_size=5000, ignore_conflicts=True)

        print('Updating question ratings...')
        ratings_question = QuestionLike.objects.filter(
            question=OuterRef('pk')
        ).values('question').annotate(
            sum_rating=Coalesce(Sum('value'), 0)
        ).values('sum_rating')

        Question.objects.filter(id__in=question_ids).update(
            rating=Coalesce(Subquery(ratings_question), 0)
        )

        print('Updating answer ratings...')
        ratings_answer = AnswerLike.objects.filter(
            answer=OuterRef('pk')
        ).values('answer').annotate(
            sum_rating=Coalesce(Sum('value'), 0)
        ).values('sum_rating')

        Answer.objects.filter(id__in=answer_ids).update(
            rating=Coalesce(Subquery(ratings_answer), 0)
        )

        print('Successfully filled the database!')
