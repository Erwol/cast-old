# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.timezone import now

# Create your models here.


from django.contrib.auth.models import AbstractUser
from django.db import models
#from exams.models import Exam


# ¡Ojo! Hay que indicar en la configuración de la app que se emplee este modelo en lugar del por defecto
class User(AbstractUser):
    # Usamos AbstractUser porque nos da los campos por defecto de un usuario en django:
    # https://docs.djangoproject.com/en/1.9/topics/auth/customizing/
    # first_name, last_name, email, password están incluidos
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    is_student = models.BooleanField(default=False, blank=True)

    is_teacher = models.BooleanField(default=False, blank=True)

    # Se usará también como username
    passport = models.CharField(max_length=30, blank=False, null=False, unique=True)

    class Meta:
        # Podríamos poner otro nombre, pero empleamos el mismo que en el sistema original
        db_table = 'auth_user'


class CenterAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    already_on_exam = models.BooleanField(default=False)
    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name

"""""
class TeacherProfile(models.Model):


    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100)

    # Un centro puede tener muchos profesores, y un profesor puede actuar sobre varios centros
    center = models.ManyToManyField(Center)

    def __str__(self):
        return self.last_name + ", " + self.first_name



class Student(models.Model):

    # Un mismo alumno puede realizar exámenes para varios centros
    centers = models.ManyToManyField(Center)

    # Un mismo alumno puede haberse examinado de múltiples convocatorias
    call = models.ManyToManyField(Call)

    # Info general
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.CharField(max_length=30, blank=False)
    passport = models.CharField(max_length=30, blank=False)
    #password = models.CharField(max_length=)

"""""