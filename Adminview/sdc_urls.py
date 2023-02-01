from django.urls import path, re_path
from . import sdc_views


# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('eln_manager', sdc_views.ElnManager.as_view(), name='scd_view_eln_manager'),
    path('eln_send_test', sdc_views.ElnFile.as_view(), name='scd_view_eln_send_file'),
    path('git_edit/<int:git_pk>', sdc_views.GitEdit.as_view(), name='scd_view_git_edit'),
    path('git_new', sdc_views.GitNew.as_view(), name='scd_view_git_new'),
    path('git_list', sdc_views.GitList.as_view(), name='scd_view_git_list'),

    path('admin_create_user', sdc_views.AdminCreateUser.as_view(), name='scd_view_admin_create_user'),
    re_path('admin_password_change/(?P<user_pk>-?[0-9]{1,10})', sdc_views.AdminPasswordChange.as_view(), name='scd_view_admin_password_change'),
    re_path('admin_edit_user/(?P<user_pk>-?[0-9]{1,10})', sdc_views.AdminEditUser.as_view(), name='scd_view_admin_edit_user'),
    path('admin_user', sdc_views.AdminUser.as_view(), name='scd_view_admin_user'),
    path('admin_main_view', sdc_views.AdminMainView.as_view(), name='scd_view_admin_main_view'),
]
