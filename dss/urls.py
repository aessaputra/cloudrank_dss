from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ahp/', views.ahp_view, name='ahp_matrix'),
]