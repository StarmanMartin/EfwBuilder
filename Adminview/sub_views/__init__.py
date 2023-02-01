def admin_user_test(request):
    return request.user.is_staff