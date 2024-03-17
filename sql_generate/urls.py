from django.urls import path
from . import views

urlpatterns = [
    path('',  views.sql, name="sql"),
    path('hash/', views.hash, name = "hash"),
    path('hash/download/', views.download_csv, name = 'down_csv')
]