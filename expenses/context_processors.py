from django.utils import timezone


def app_globals(request):
    """
    Context processor providing global variables to all templates.
    """
    today = timezone.localdate()
    return {
        "today_date": today,
        "today_display": today.strftime("%A, %d %B %Y"),
        "app_title": "SpendWise",
        "app_tagline": "Because money shouldn't just vanish",
    }
