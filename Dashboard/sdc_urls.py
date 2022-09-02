from django.urls import path, re_path
from . import sdc_views


# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('efw_list', sdc_views.EfwList.as_view(), name='scd_view_efw_list'),
    path('efw_edit/<int:efw_pk>', sdc_views.EfwEdit.as_view(), name='scd_view_efw_edit'),
    path('efw_new', sdc_views.EfwNew.as_view(), name='scd_view_efw_new'),
    path('main_view', sdc_views.MainView.as_view(), name='scd_view_main_view'),

    path('efw_download/<int:efw_pk>', sdc_views.EfwDownload.as_view(), name='scd_view_efw_download'),
]
