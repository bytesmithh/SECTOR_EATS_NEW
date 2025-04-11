from django.urls import path
from . import views

urlpatterns=[
    path("",views.home_view,name="home"),
    path("signup/",views.signup_view,name="signup_view"),
    path("login/",views.login_view,name="login_view"),
    path('about_us/',views.about_us_view,name="about_us_view"),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path("chatbot/", views.chatbot_page, name="chatbot_page"),
    path('logout/', views.logout_view, name='logout'),
    path("admindashboard/",views.admin_dashboard,name="admin_dashboard"),
    path('admindashboard/add_restaurant/', views.add_restaurant, name='add_restaurant'),
    path('restaurants/', views.list_restaurants, name='list_restaurants'),
    path('admindashboard/edit_restaurant/<int:restaurant_id>/', views.edit_restaurant, name='edit_restaurant'),
    path('admindashboard/delete_restaurant/<int:restaurant_id>/', views.delete_restaurant, name='delete_restaurant'),

    path('user_dashboard/',views.user_dashboard_view,name="user_dashboard_view"),
   path('admin/restaurant/<int:restaurant_id>/add-menu/', views.add_menu_item, name='add_menu_item'),
   path('restaurant/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),

   path('menu/<int:item_id>/edit/', views.edit_menu_item_view, name='edit_menu_item'),
    path('menu/<int:item_id>/delete/', views.delete_menu_item_view, name='delete_menu_item'),







]

