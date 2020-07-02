from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    url(r'^$', views.basic, name='basic'),
    url(r'^manual/$', views.manual, name='manual'),
    url(r'^field/$', views.field, name='field'),
    url(r'^attrs/$', views.attrs, name='attrs'),
    url(r'^tweaks/$', views.tweaks, name='tweaks'),
    url(r'^bootstrap4/$', views.bootstrap4, name='bootstrap4'),
    url(r'^user/$', views.user, name='user'),
    path('success/', views.success, name='success'),
    path('initiatePayment/', views.initiatePayment, name='initiatePayment'),
    path('handleShopperRedirect/', views.handleShopperRedirect, name='handleShopperRedirect'),
    path('submitAdditionalDetails/', views.submitAdditionalDetails, name='submitAdditionalDetails'),
    path('error/', views.error, name='error'),
    path('pending/', views.pending, name='pending'),
    path('failed/', views.failed, name='failed'),
    path('checkout/', views.checkout, name='checkout'),
]
