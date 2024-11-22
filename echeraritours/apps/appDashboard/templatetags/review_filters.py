from django import template
from apps.appTour.models import Reviews

register = template.Library()


@register.filter
def get_review(reservation_id, reviews):
    """
    Author: Santiago Mendivil
    Retrieve a review based on the reservation ID.

    Args:
        reservation_id (int): The ID of the reservation for which the review is being retrieved.
        reviews (QuerySet): A Django QuerySet containing review objects.

    Returns:
        Review: The review object corresponding to the given reservation ID, or None if no such review exists.

    Raises:
        Reviews.DoesNotExist: If no review with the given reservation ID is found in the QuerySet.
    """
    try:
        return reviews.get(reservation_id=reservation_id)
    except Reviews.DoesNotExist:
        return None
