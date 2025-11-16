import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.db import transaction
from questions.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from django.contrib.auth.models import User

class Command(BaseCommand):
  help = 'Fills the database with test data based on a given ratio.'

  def add_arguments(self, parser):
    parser.add_argument('ratio', type=int, help='The ratio for data generation.')

  @transaction.atomic
  def handle(self, *args, **options):
    ratio = options['ratio']
    fake = Faker()

    print(f'Starting to fill database with ratio: {ratio}...')

    print('Creating users and profiles...')
    users = [User(username=fake.unique.user_name(), password='password123') for _ in range(ratio)]
    User.objects.bulk_create(users)
    profiles = [Profile(user=user) for user in users]
    Profile.objects.bulk_create(profiles)

    print('Creating tags...')
    tags = [Tag(name=fake.unique.word()) for _ in range(ratio)]
    Tag.objects.bulk_create(tags)

    print('Creating questions...')
    questions = []
    for _ in range(ratio * 10):
      question = Question(
        author=random.choice(profiles),
        title=fake.sentence(nb_words=5),
        text=fake.paragraph(nb_sentences=3)
      )
      questions.append(question)
    Question.objects.bulk_create(questions)

    print('Adding tags to questions...')
    all_questions = list(Question.objects.all())
    for question in all_questions:
      question.tags.set(random.sample(tags, k=random.randint(1, 4)))

    print('Creating answers...')
    answers = []
    for _ in range(ratio * 100):
      answer = Answer(
        author=random.choice(profiles),
        question=random.choice(all_questions),
        text=fake.paragraph(nb_sentences=2)
      )
      answers.append(answer)
    Answer.objects.bulk_create(answers)

    print('Creating likes...')
    all_answers = list(Answer.objects.all())
    
    question_likes_to_create = []
    question_like_pairs = set()
    for _ in range(ratio * 100):
      profile = random.choice(profiles)
      question = random.choice(all_questions)
      if (profile.id, question.id) not in question_like_pairs:
        question_likes_to_create.append(QuestionLike(user=profile, question=question, value=random.choice([1, -1])))
        question_like_pairs.add((profile.id, question.id))
    QuestionLike.objects.bulk_create(question_likes_to_create, ignore_conflicts=True)

    answer_likes_to_create = []
    answer_like_pairs = set()
    for _ in range(ratio * 100):
      profile = random.choice(profiles)
      answer = random.choice(all_answers)
      if (profile.id, answer.id) not in answer_like_pairs:
        answer_likes_to_create.append(AnswerLike(user=profile, answer=answer, value=random.choice([1, -1])))
        answer_like_pairs.add((profile.id, answer.id))
    AnswerLike.objects.bulk_create(answer_likes_to_create, ignore_conflicts=True)

    print('Successfully filled the database!')
