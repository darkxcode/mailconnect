from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
import time

class EmailRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/send-campaign/'):
            user_key = f'email_rate_limit_{request.user.id}'
            current_time = time.time()
            
            # Get email sending history
            history = cache.get(user_key, [])
            
            # Remove old entries
            history = [t for t in history if t > current_time - 60]
            
            # Check rate limit
            if len(history) >= settings.EMAIL_RATE_LIMIT['emails_per_minute']:
                return HttpResponseTooManyRequests('Email rate limit exceeded')
            
            # Add current request
            history.append(current_time)
            cache.set(user_key, history, 60)
        
        return self.get_response(request) 