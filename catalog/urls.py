from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('order/submit/', views.submit_order, name='submit_order'),
    path('order/<str:order_number>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order/<str:order_number>/invoice/', views.invoice_print, name='invoice_print'),
    path('order/<str:order_number>/invoice/pdf/', views.invoice_pdf, name='invoice_pdf'),
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
    # Order management (admin)
    path('manage/orders/', views.order_list, name='order_list'),
    path('manage/orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('manage/orders/<str:order_number>/delete/', views.order_delete, name='order_delete'),
]
