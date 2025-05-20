from django.conf import settings

def supabase_settings(request):
    return {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    }
