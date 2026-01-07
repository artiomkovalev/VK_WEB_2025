import jwt
import time
import json
import requests
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.conf import settings

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

def get_centrifugo_token(user_id):
    sub = str(user_id) if user_id else "UNAUTH"
    claims = {
        "sub": sub,
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(claims, settings.CENTRIFUGO_HMAC_SECRET, algorithm="HS256")

def publish_to_centrifugo(channel, data):
    command = {
        "method": "publish",
        "params": {
            "channel": channel,
            "data": data
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': settings.CENTRIFUGO_API_KEY
    }
    try:
        response = requests.post(
            settings.CENTRIFUGO_API_URL,
            data=json.dumps(command),
            headers=headers,
            timeout=1
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Centrifugo publish error: {e}")
        return False
