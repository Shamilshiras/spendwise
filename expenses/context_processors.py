from django.utils import timezone


def app_globals(request):
    today = timezone.localdate()
    return {
        "today_date": today,
        "today_display": today.strftime("%A, %d %B %Y"),
        "app_title": "SpendWise",
        "app_tagline": "Because money shouldn't just vanish",
    }
