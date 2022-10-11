from django.urls import path
from . import sdc_views


# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('file_tree', sdc_views.FileTree.as_view(), name='scd_view_file_tree'),
    path('uml_change/<int:dia_pk>', sdc_views.UmlChange.as_view(), name='scd_view_uml_change'),
    path('uml_list', sdc_views.UmlList.as_view(), name='scd_view_uml_list'),
    path('uml_create', sdc_views.UmlCreate.as_view(), name='scd_view_uml_create'),
    path('uml_info', sdc_views.UmlInfo.as_view(), name='scd_view_uml_info'),
    path('uml_editor/<int:dia_pk>', sdc_views.UmlEditor.as_view(), name='scd_view_uml_editor'),
    path('efw_list', sdc_views.EfwList.as_view(), name='scd_view_efw_list'),
    path('efw_edit/<int:efw_pk>', sdc_views.EfwEdit.as_view(), name='scd_view_efw_edit'),
    path('efw_new/<str:type>', sdc_views.EfwNew.as_view(), name='scd_view_efw_new'),
    path('main_view', sdc_views.MainView.as_view(), name='scd_view_main_view'),

    path('efw_download/<int:efw_pk>', sdc_views.EfwDownload.as_view(), name='scd_view_efw_download'),
]
