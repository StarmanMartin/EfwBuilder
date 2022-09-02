from django.urls import path, re_path
from . import sdc_views

# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('start_view', sdc_views.StartView.as_view(), name='scd_view_start_view'),
]
