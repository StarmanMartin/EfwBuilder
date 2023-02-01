from django.urls import path, re_path
from . import sdc_views

# Do not add an app_name to this file

urlpatterns = [
    # scd view below
    path('user_logout', sdc_views.UserLogout.as_view(), name='scd_view_user_logout'),
    path('user_manager', sdc_views.UserManager.as_view(), name='scd_view_user_manager'),
    path('login_view', sdc_views.LoginView.as_view(), name='scd_view_login_view'),
]
