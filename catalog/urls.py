from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('vegetables/<int:pk>/', views.vegetable_detail, name='vegetable_detail'),
    # Banner management (staff)
    path('manage/banners/', views.banner_list, name='banner_list'),
    path('manage/banners/add/', views.banner_create, name='banner_create'),
    path('manage/banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('manage/banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),
    path('manage/banners/<int:pk>/toggle/', views.banner_toggle, name='banner_toggle'),
    # Vegetable management (admin)
    path('manage/vegetables/', views.vegetable_list, name='vegetable_list'),
    path('manage/vegetables/add/', views.vegetable_create, name='vegetable_create'),
    path('manage/vegetables/<int:pk>/edit/', views.vegetable_edit, name='vegetable_edit'),
    path('manage/vegetables/<int:pk>/delete/', views.vegetable_delete, name='vegetable_delete'),
    path('manage/vegetables/<int:pk>/toggle/', views.vegetable_toggle, name='vegetable_toggle'),
    # Site content editing
    path('manage/content/<str:section>/edit/', views.section_edit, name='section_edit'),
    # Contact info editing
    path('manage/contact/edit/', views.contact_edit, name='contact_edit'),
]
