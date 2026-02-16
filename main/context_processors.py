from django.contrib.auth.models import User
from .models import Test, CheckTest

def footer_stats(request):
    """Provide counts for footer statistics across all templates."""
    try:
        total_tests_count = Test.objects.count()
    except Exception:
        total_tests_count = 0

    try:
        active_users_count = User.objects.filter(is_active=True).count()
    except Exception:
        active_users_count = 0

    try:
        completed_tests_count = CheckTest.objects.count()
    except Exception:
        completed_tests_count = 0

    return {
        'total_tests_count': total_tests_count,
        'active_users_count': active_users_count,
        'completed_tests_count': completed_tests_count,
    }
