from django.http import HttpResponse
from django.urls import reverse
from sdc_tools.django_extension.response import sdc_link_obj_factory


def response_error_handler(request, exception=None):
    return HttpResponse('Error handler content', status=403)

def my_custom_page_not_found_view(request, exception=None):
    return HttpResponse('Error handler content', status=403)

def my_custom_permission_denied_view(request, exception=None):
    return my_custom_error_view(request, exception and 403)

def my_custom_error_view(request, exception=None):
    url = '<error data-code="{}"></error>'.format(403)
    return  HttpResponse(url, status=exception)

def my_custom_bad_request_view(request, exception=None):
    return HttpResponse('Error handler content', status=403)