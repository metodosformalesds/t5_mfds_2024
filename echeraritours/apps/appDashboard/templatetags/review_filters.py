from django import template
from apps.appTour.models import Reviews

register = template.Library()


@register.filter
def get_review(reservation_id, reviews):
    try:
        return reviews.get(reservation_id=reservation_id)
    except Reviews.DoesNotExist:
        return None
