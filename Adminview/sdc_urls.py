from django.urls import path, re_path
from . import sdc_views
from .sub_views import user_view

# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('git_edit/<int:git_pk>', sdc_views.GitEdit.as_view(), name='scd_view_git_edit'),
    path('git_new', sdc_views.GitNew.as_view(), name='scd_view_git_new'),
    path('git_list', sdc_views.GitList.as_view(), name='scd_view_git_list'),

    path('admin_create_user', user_view.AdminCreateUser.as_view(), name='scd_view_admin_create_user'),
    re_path('admin_password_change/(?P<user_pk>-?[0-9]{1,10})', user_view.AdminPasswordChange.as_view(), name='scd_view_admin_password_change'),
    re_path('admin_edit_user/(?P<user_pk>-?[0-9]{1,10})', user_view.AdminEditUser.as_view(), name='scd_view_admin_edit_user'),
    path('admin_user', user_view.AdminUser.as_view(), name='scd_view_admin_user'),
    path('admin_main_view', sdc_views.AdminMainView.as_view(), name='scd_view_admin_main_view'),
]
