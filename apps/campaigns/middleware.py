from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

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
        # If DEBUG is True, redirect HTTPS to HTTP
        if settings.DEBUG and request.is_secure():
            url = request.build_absolute_uri(request.get_full_path())
            url = url.replace('https://', 'http://')
            return HttpResponseRedirect(url)
        
        return self.get_response(request)

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        url_name = resolve(path).url_name

        # List of URLs that require authentication
        authenticated_urls = ['dashboard', 'campaigns', 'profile', 'settings', 'prospects', 'templates', 'reports']

        # Check if URL requires authentication and user is not authenticated
        if url_name in authenticated_urls and not request.user.is_authenticated:
            return redirect('login')

        response = self.get_response(request)
        return response