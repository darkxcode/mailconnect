from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add rate limiting logic here if needed
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, RateLimitExceeded):
            return HttpResponseTooManyRequests("Too many requests. Please try again later.")
        return None

class RateLimitExceeded(Exception):
    pass

class HttpsRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only redirect in production
        if not settings.DEBUG and not request.is_secure():
            return self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        if not request.is_secure():
            return self.get_response(request)
        return self.get_response(request)