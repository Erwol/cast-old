# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = 'web'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^buscarPelicula/', views.resultados, name='buscarPeli'),
    #url(r'^estadisticas/', views.generar_grafica, name='generar_estadisticas'),
    #url(r'^(?P<pk>[0-9]+)/votar/$', views.votar, name='votar'),
]