# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = 'exam'
urlpatterns = [
    url(r'^exam/validatekey/', views.validate_key, name='validate_key'),

    url(r'^exam/chooseavatar/', views.choose_avatar, name='choose_avatar'),

    url(r'^exam/authentication/avatar=(?P<avatar_id>\d+)$', views.authentication, name='authentication'),

    url(r'^exam/part/', views.load_part, name='load_part'),

    url(r'^exam/element/', views.load_element, name='load_element'),

    url(r'^exam/question/', views.load_question, name='load_question'),

    url(r'exam/slw/', views.load_slw, name='load_slw'),

    url(r'exam/slwq/', views.load_slw_question, name='load_slw_question'),

    url(r'exam/topics/', views.load_topics, name='load_topics'),

    url(r'exam/expressions/topic=(?P<topic_id>\d+)$', views.load_topic_expressions, name='load_topic_expressions'),

    url(r'^exam/over', views.the_end, name='the_end'),
]