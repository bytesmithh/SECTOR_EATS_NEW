from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')

        if hasattr(request.user, 'profile'):
            if request.user.profile.role == 'restaurant_admin':
                return view_func(request, *args, **kwargs)
        return redirect('user_dashboard_view')  # Make sure this route exists
    return wrapper
