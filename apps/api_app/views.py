from django.http import JsonResponse

def index(request):
    return JsonResponse({'message': 'Welcome to the API!'}) 