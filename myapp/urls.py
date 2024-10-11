from django.urls import path
from . import views
from django.contrib import auth


# app_name = 'userauths'

urlpatterns = [
    path("sign-up/", views.Registerview, name="sign-up"),
    path("sign-in/", views.login_view, name="login"),
    path('two_fa_input/<int:user_id>/', views.two_fa_input_view, name='two_fa_input'),
    path("sign-out/", views.logout_view, name="logout"),
    path('kyc/', views.kyc_registration, name='kyc_register'),
    path('dashboard/', views.dashboard, name='dashboard')
]


