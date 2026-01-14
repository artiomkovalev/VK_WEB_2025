from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from questions.models import Tag, User

class Command(BaseCommand):
    help = 'Calculates popular tags and best members and caches them'

    def handle(self, *args, **options):
        print("Starting stats calculation...")

        three_months_ago = timezone.now() - timedelta(days=90)
        popular_tags = Tag.objects.filter(
            question__created_at__gte=three_months_ago
        ).annotate(
            num_recent_questions=Count('question')
        ).order_by('-num_recent_questions')[:10]

        one_week_ago = timezone.now() - timedelta(days=7)
        
        best_members = User.objects.filter(
            Q(answer__created_at__gte=one_week_ago) | Q(question__created_at__gte=one_week_ago)
        ).annotate(
            activity_count=Count('answer', distinct=True) + Count('question', distinct=True)
        ).order_by('-activity_count')[:10]

        cache.set('popular_tags', list(popular_tags), timeout=None)
        cache.set('best_members', list(best_members), timeout=None)

        print(f"Cached {len(popular_tags)} tags and {len(best_members)} members")
