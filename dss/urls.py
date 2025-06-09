from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ahp/', views.ahp_view, name='ahp_matrix'),
    path('topsis/input/', views.topsis_input_view, name='topsis_input'),
    path('topsis/results/', views.topsis_results_view, name='topsis_results'),
    path('kriteria/', views.kriteria_list_view, name='kriteria_list'),
    path('kriteria/tambah/', views.kriteria_create_view, name='kriteria_create'),
    path('kriteria/edit/<int:pk>/', views.kriteria_update_view, name='kriteria_update'),
    path('kriteria/hapus/<int:pk>/', views.kriteria_delete_view, name='kriteria_delete'),
    path('alternatif/', views.alternatif_list_view, name='alternatif_list'),
    path('alternatif/tambah/', views.alternatif_create_view, name='alternatif_create'),
]