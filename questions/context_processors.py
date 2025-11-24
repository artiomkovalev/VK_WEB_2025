from .models import Tag

def global_settings(request):
    return {
        'popular_tags': Tag.objects.popular(),
    }
