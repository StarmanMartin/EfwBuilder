from django.core.exceptions import PermissionDenied
from django.shortcuts import render


class PermissionDeniedErrorHandler:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # This is the method that responsible for the safe-exception handling
        if isinstance(exception, PermissionDenied):
            ref = request.META.get('HTTP_REFERER').split('~', 1)
            context = {'next': ref[-1]}
            return render(
                request=request,
                template_name="403.html",
                context=context,
                status=200
            )
        return None