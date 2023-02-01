from django.urls import path
from . import sdc_views


# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('basic_info', sdc_views.BasicInfo.as_view(), name='scd_view_basic_info'),
    path('file_tree', sdc_views.FileTree.as_view(), name='scd_view_file_tree'),
    path('efw_list', sdc_views.EfwList.as_view(), name='scd_view_efw_list'),
    path('efw_edit/<int:efw_pk>', sdc_views.EfwEdit.as_view(), name='scd_view_efw_edit'),
    path('efw_new/<str:type>', sdc_views.EfwNew.as_view(), name='scd_view_efw_new'),
    path('main_view', sdc_views.MainView.as_view(), name='scd_view_main_view'),

    path('efw_download/<int:efw_pk>', sdc_views.EfwDownload.as_view(), name='scd_view_efw_download'),
]
