from django.urls import path
from . import views

app_name = 'docs'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('article/<slug:slug>/', views.article, name='article'),
] 