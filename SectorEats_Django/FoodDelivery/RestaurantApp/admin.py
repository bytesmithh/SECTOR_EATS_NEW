from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import Profile, Restaurant

admin.site.site_header = "Sector Eats Administration"
admin.site.site_title = "Sector Eats Admin"
admin.site.index_title = "Welcome to Sector Eats Admin Panel"

admin.site.register(Profile)
admin.site.register(Restaurant)




