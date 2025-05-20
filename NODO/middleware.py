from django.shortcuts import redirect
from django.conf import settings

class RestrictAppMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/administracion/'):  
            if not (request.user.is_authenticated and request.user.is_staff):
                return redirect(settings.LOGIN_URL)

        return self.get_response(request)
