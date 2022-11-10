from django.urls import path, re_path
from . import sdc_views

# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    re_path('search_select_input/(?P<model>.+)/(?P<value>[0-9,]*)', sdc_views.SearchSelectInput.as_view(), name='scd_view_search_select_input'),
    re_path('error/(?P<code>[0-9]{3})', sdc_views.Error.as_view(), name='scd_view_error'),
    path('fof', sdc_views.Fof.as_view(), name='scd_view_fof'),
    path('download/file_exporter_task.vbs', sdc_views.DownloadVbs.as_view(), name='file_exporter_task.vbs'),
    path('download/efw.service', sdc_views.DownloadService.as_view(), name='file_efw.service'),

]
