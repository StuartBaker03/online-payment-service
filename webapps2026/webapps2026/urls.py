"""
URL configuration for webapps2026 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from payapp import views as payapp_views
from register import views as register_views
from payappadmin import views as payappadmin_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('register/', register_views.register_user, name='register'),
    path('login/', register_views.login_user, name='login'),
    path('logout/', register_views.logout_user, name='logout'),
    path("home/", payapp_views.home, name='home'),
    path("directpayment/", payapp_views.direct_payment, name='direct_payment' ),
    path("paymenthistory/", payapp_views.payment_history, name='payment_history'),
    path("requestpayment/", payapp_views.request_payment, name='request_payment' ),
    path("requesthistory/", payapp_views.request_history, name='request_history'),
    path("acceptrequest/<int:request_id>/", payapp_views.accept_request, name='accept_request'),
    path("rejectrequest/<int:request_id>/", payapp_views.reject_request, name='reject_request'),
    path("adminhome/", payappadmin_views.admin_home, name='admin_home'),
    path("adminviewaccounts/", payappadmin_views.admin_view_accounts, name='admin_view_accounts'),
    path("adminviewpayments/", payappadmin_views.admin_view_payments, name='admin_view_payments'),
    path("adminviewrequests/", payappadmin_views.admin_view_requests, name='admin_view_requests'),
    path("registeradmin/", payappadmin_views.register_admin, name='register_admin'),
    path("api-auth/", include('rest_framework.urls')),
    path("webapps2026/", include('currencyconversion.urls')),
]
