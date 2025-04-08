from django.urls import path
from . import views

urlpatterns=[
    path("",views.home_view,name="home"),
    path("signup/",views.signup_view,name="signup_view"),
    path("login/",views.login_view,name="login_view"),
    path('about_us/',views.about_us_view,name="about_us_view"),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path("chatbot/", views.chatbot_page, name="chatbot_page"),


]

