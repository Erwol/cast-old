from django.shortcuts import render, redirect
from .models import *
from exam.models import Exam, Call, Avatar
from .forms import *
# https://docs.djangoproject.com/en/1.9/topics/auth/passwords/#module-django.contrib.auth.hashers
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
# Create your views here.
from django.core.mail import send_mail

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from exam.models import Part, Call, Exam

"""""
if form.is_valid():
    subject = form.cleaned_data['subject']
    message = form.cleaned_data['message']
    sender = form.cleaned_data['sender']
    cc_myself = form.cleaned_data['cc_myself']

    recipients = ['info@example.com']
    if cc_myself:
        recipients.append(sender)

    send_mail(subject, message, sender, recipients)
    return HttpResponseRedirect('/thanks/')
"""""


def exam_login(request):
    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/
    if request.method == "POST":
        exam_id = request.session['exam_id']
        call_id = request.session['call_id']
        avatar_id = request.session['call_id']

        # El usuario y el email será lo mismo
        # num_results = StudentProfile.objects.filter(user__username=request.POST['email']).count()

        form = StudentLogInForm(request.POST)

        if form.is_valid():
            request.session['student_id'] = User.objects.get(username=form.cleaned_data['email']).id
            return HttpResponseRedirect(reverse('exam:load_part'))
        else:
            return render(request, 'user/exam_authentication.html', {
                'signup_form': StudentSignUpForm,
                'login_form': form,
                'progress': 10,
                'exam': Exam.objects.get(pk=exam_id),
                'call': Call.objects.get(pk=call_id),
                'avatar': Avatar.objects.get(pk=avatar_id),
            })
    else:
        return render(request, 'user/exam_authentication.html', {
            'signup_form': StudentSignUpForm,
            'login_form': StudentLogInForm,
            'progress': 10,
        })


def exam_registration(request):
    if request.method == "POST":
        # TODO Mandar email con enlace a crear una contraseña. Mientras tanto, contraseña 1234
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User(
                first_name=str(cd['first_name']),
                last_name=str(cd['last_name']),
                email=str(cd['email']),
                # https://docs.djangoproject.com/en/1.9/topics/auth/passwords/
                # http://stackoverflow.com/questions/9480641/django-password-generator
                #password=User.objects.make_random_password(),
                username=str(cd['email']),
                passport=str(cd['passport']),
                is_student=True
            )
            user.set_password(1234)
            user.save()
            student = StudentProfile(user=user)
            student.save()
            request.session['student_id'] = user.id
            # Se le pueden añadir argumentos con args
            return HttpResponseRedirect(reverse('exam:load_part',))

    else:
        return render(request, 'user/exam_authentication.html', {
            'signup_form': StudentSignUpForm,
            'login_form': StudentLogInForm,
            'progress': 10,
        })