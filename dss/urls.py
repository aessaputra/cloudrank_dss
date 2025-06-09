from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ahp/', views.ahp_view, name='ahp_matrix'),
    path('topsis/input/', views.topsis_input_view, name='topsis_input'),
    path('topsis/results/', views.topsis_results_view, name='topsis_results'),
]