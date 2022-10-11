"""EfwBuilder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.shortcuts import render
from django.conf import settings
from django.views.i18n import JavaScriptCatalog

from WebDAV.view import DavView, DavDownloadView

urlpatterns = [
    re_path('sdc_view/sdc_tools/', include('sdc_tools.sdc_urls')),
    re_path('sdc_view/sdc_user/', include('sdc_user.sdc_urls')),
    # scd view below
    path('sdc_view/dashboard/', include('Dashboard.sdc_urls')),
    path('sdc_view/utils/', include('Utils.sdc_urls')),
    path('sdc_view/adminview/', include('Adminview.sdc_urls')),
    path('sdc_view/logedout/', include('Logedout.sdc_urls')),

    path('admin/', admin.site.urls),
    re_path('download/webdav(?P<path>.*)', DavDownloadView.as_view(), name="download_webdav"),
    re_path('webdav/(?P<name>[^/]*)/(?P<path>.*)', DavView.as_view(), name="webdav"),
]

def main_index(request):
    if request.user.is_authenticated:
        return render(request, 'EfwBuilder/main.html', {'VERSION': settings.VERSION})
    return render(request, 'EfwBuilder/index.html', {'VERSION': settings.VERSION})


urlpatterns += [
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('', main_index, name='index'),
    path('main', main_index, name='sdc_index'),
    re_path('^main/.*', main_index, name='sdc_index'),
]

handler404 = 'Utils.views.my_custom_page_not_found_view'
handler500 = 'Utils.views.my_custom_error_view'
handler403 = 'Utils.views.my_custom_permission_denied_view'
handler400 = 'Utils.views.my_custom_bad_request_view'
