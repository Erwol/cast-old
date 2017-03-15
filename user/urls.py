# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = 'user'
urlpatterns = [
    url(r'^examsignin/', views.exam_login, name='exam_sign_in'),
    url(r'^examsignup/', views.exam_registration, name='exam_sign_up'),
]