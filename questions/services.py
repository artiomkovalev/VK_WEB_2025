from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404

from questions.models import Answer

def toggle_vote(user, obj, like_model_class, related_field_name, vote_value):
    if user == obj.author:
        raise ValidationError("You can't vote on your own content")
    with transaction.atomic():
        filter_kwargs = {'user': user, related_field_name: obj}
        try:
            like = like_model_class.objects.select_for_update().get(**filter_kwargs)
            if like.value == vote_value:
                like.delete()
            else:
                like.value = vote_value
                like.save()
        except like_model_class.DoesNotExist:
            like_model_class.objects.create(value=vote_value, **filter_kwargs)
        rating_result = like_model_class.objects.filter(**{related_field_name: obj}).aggregate(total=Sum('value'))
        new_rating = rating_result['total'] or 0
        obj.rating = new_rating
        obj.save(update_fields=['rating'])
        return new_rating
