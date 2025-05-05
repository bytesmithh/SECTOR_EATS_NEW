from django.urls import path
from . import views

urlpatterns = [
    path('feedback/', views.submit_feedback, name='feedback'),
    path('thank-you/', views.thank_you, name='thank_you'), 
]
