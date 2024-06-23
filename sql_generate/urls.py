from django.urls import path
from . import views

urlpatterns = [
    path('',  views.sql, name="sql_generation"),
    path('hash/', views.hash, name = "hash"),
    path('coordinates/', views.coordinates_generator, name='coordinates'),
    path('map_geohashes/', views.map_geohashes, name = 'map_geohashes'),
    path('map_marker', views.map_marker, name = 'map_marker'),
    path('hash/download/', views.download_csv, name = 'down_csv')
]