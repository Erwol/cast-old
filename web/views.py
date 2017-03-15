# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import *
from django.utils.timezone import utc
from datetime import datetime
from threading import Thread
# Create your views here.


def index(request):
    return render(request, 'web/index.html', {
        'page_title': 'Home',
    })