from django.urls import path
from .views import *
from . import views

app_name = 'userauth'

urlpatterns = [
   path('custom_logout/', custom_logout, name='custom_logout'),
    path('register/', views.customer_register, name='register'),
    path('home/', views.home, name='home'),
    path('about/',about,name='about'),
    path('contact/', views.contact, name='contact'),
    path('category/<str:category>',categoryView.as_view(),name='category'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('booking/', views.booking_page, name='booking-page'),



     
]