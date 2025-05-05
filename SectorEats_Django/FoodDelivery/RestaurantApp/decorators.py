from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import Profile
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:

            return redirect('/login/')

        if hasattr(request.user, 'profile'):
            if request.user.profile.role == 'restaurant_admin':
                return view_func(request, *args, **kwargs)
        messages.error(request, "Users are not allowed to access the admin portal.")
        return redirect('user_dashboard_view')  # Make sure this route exists
    return wrapper

def user_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('login_view')

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('login_view')

        if user.is_staff or profile.role == 'restaurant_admin':
            messages.error(request, "Admins are not allowed to access the user portal.")
            return redirect('login_view')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
