from django.urls import path

from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgot/', views.forgot_password, name='forgot'),
    path('logout/', views.logout_user, name='log_out'),
    path('phone_verification/', views.verify_phone_number, name='phone_verification'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('loans/', views.loans, name='loans'),
    path('notification/<str:sender>/<int:id>', views.notification, name='notification'),
    path('logs/', views.logs, name='logs'),
    path('transactions/', views.transactions, name='transactions'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('change-number/', views.change_number, name='change_number'),

    path('ad_min/', views.admin, name='admin'),
    path('edit_user/<str:username>/', views.edit_user, name='edit_user'),
    path('loan_application', views.loan_application, name='loan_application'),
    path('loan_repayment', views.loan_repayment, name='loan_repayment'),
    path('monthly_contributions', views.contribution, name='contribution'),
    path('loan_repay/<str:username>/', views.loan_repay, name='repay'),
    path('approve_user/<str:username>/', views.approve_user, name='approve_user'),
    path('reject_user/<str:username>/', views.reject_user, name='reject_user'),

]
