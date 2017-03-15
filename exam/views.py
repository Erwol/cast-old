from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import *
from user.models import User, StudentProfile, TeacherProfile
from user.forms import StudentSignUpForm, StudentLogInForm
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import random


def get_ip_address(request):
    """ use requestobject to fetch client machine's IP Address """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')    ### Real IP address of client Machine
    return ip


# TODO Mejorar con formulario
def validate_key(request):
    if request.method == "POST":
        if 'call_pass' in request.POST:
            call_pass = request.POST['call_pass']
            num_results = Call.objects.filter(password=call_pass).count()

            if num_results == 1:
                # Podemos buscar por la clave porque es única
                call = Call.objects.get(password=call_pass)

                # Iniciamos la sesión custom
                exam_session = Session(
                    ip=get_ip_address(request),
                    call=Call.objects.get(pk=call.id)
                )
                exam_session.save()
                request.session['session_id'] = exam_session.id
                request.session['call_id'] = call.id
                request.session['exam_id'] = call.exam.id
                request.session['actual_part'] = 0
                request.session['last_part'] = Part.objects.filter(exam=call.exam).count()

                return HttpResponseRedirect(reverse('exam:choose_avatar'))#, args=(call.exam.id, call.id,)))
            else:
                return render(request, 'web/index.html', {
                    # 'completed': 10,
                    'error_message': "003 - Call error.",
                    'error_description': "You entered a wrong exam password. Please, try again.",
                })
        else:
            return render(request, 'web/index.html', {
                'error_message': "002 - Can't validate the key.",
                'error_description': "It seems you didn't enter a valid any key.",
            })
    else:
        return render(request, 'web/index.html', {
            'error_message': "001 - Can't validate the key.",
            'error_description': "It seems you accesed this page through an uncontrolled way. Please, try to enter your exam key again.",
        })


def choose_avatar(request):

    call = Call.objects.get(pk=request.session['call_id'])

    return render(request, 'exam/index.html', {
        'call': call,
        'exam': call.exam,
        # Buscamos todos los avatares disponibles para todas las voces de que dispone el examen
        'avatars': Avatar.objects.filter(voice__in=call.exam.voices.all()),
        'progress': 5,
        'equalizer': 0,
    })


# TODO Controlar POST
def authentication(request, avatar_id):

    # TODO Añadir seguridad
    request.session['avatar_id'] = avatar_id
    session = Session.objects.get(pk=request.session['session_id'])
    session.avatar = Avatar.objects.get(pk=avatar_id)
    session.save()

    return render(request, 'user/exam_authentication.html', {
        'exam': Exam.objects.get(pk=request.session['exam_id']),
        'call': Call.objects.get(pk=request.session['call_id']),
        'avatar': Avatar.objects.get(pk=avatar_id),
        'signup_form': StudentSignUpForm,
        'login_form': StudentLogInForm,
        'progress': 10,
    })




def get_progress(request):
    actual_element = request.session['actual_element']
    exam = request.session['exam_id']
    exam_parts = Part.objects.filter(exam=exam)
    last_element = Element.objects.filter(part__in=exam_parts).count()

    return (actual_element * 100) / last_element


# TODO Seguridad
# Método que se encarga de cargar todas las partes del examen
def load_part(request):

    actual_part = request.session['actual_part']
    # Autocalculado --> last_part = request.session['last_part']
    actual_call = request.session['call_id']

    if actual_part < Part.objects.filter(exam=request.session['exam_id']).count():

        # Aumentamos en uno la parte actual. No influye ya que tb lo tenemos guardado en actual_part
        #request.session['actual_part'] += 1

        # Cargamos la convocatoria de examen
        call = Call.objects.get(pk=actual_call)

        # Cargamos la parte actual del examen, ordenada en orden ascendente 1 ... 2... 3 etc
        part = Part.objects.filter(exam=call.exam).order_by('order')

        # Nos quedamos sólo con la parte actual
        # TODO Mejorar rendimiento de la llamada de arriba
        part = part[actual_part]

        # Guardamos la id de la parte actual
        request.session['actual_part_id'] = part.id

        # Aun quedan partes del examen por realizar
        request.session['actual_element'] = 0

        # El último elemento de todos los que esta parte del examen tiene
        # request.session['last_element'] = Element.objects.filter(part=part).count()

        return render(request, 'exam/part_welcome.html', {
            'exam': Exam.objects.get(pk=request.session['exam_id']),
            'avatar': Avatar.objects.get(pk=request.session['avatar_id']),
            'call': call,
            'part': part,
            'element': Element.objects.filter(part=part).order_by('order')[0],
            'progress': 15,
        })

    else:
        # TODO Borrar todos los restos de sesión
        return HttpResponseRedirect(reverse('exam:the_end'))


# Función encargada de gestionar todos los tipos de elementos
def load_element(request):
    actual_part_id = request.session['actual_part_id']

    actual_element = int(request.session['actual_element'])

    # Pasamos al siguiente elemento. Recordar que esto sólo es el orden inicializado a 0 en el inicio de cada parte
    request.session['actual_element'] += 1

    if actual_element < Element.objects.filter(part=request.session['actual_part_id']).count():

        # De todos los elementos que conformen esta parte cargamos sólo el actual (0, 1, 2... n)
        element = Element.objects.filter(part=actual_part_id).order_by('order')[actual_element]

        request.session['actual_element_id'] = element.id

        if element.is_question:
            """""
                Esta clase de elemento es una simple pregunta que se carga desde load_question
            """""
            request.session['question_to_load_id'] = Question.objects.get(element=element).id
            return HttpResponseRedirect(reverse('exam:load_question'))

        elif element.is_questions_group:
            """""
                La función de este tipo de elemento es seleccionar de entre un grupo de elementos de tipo pregunta una
                de ellas y cargarla mediante la función load_question.

                1: Se carga el grupo que esté enlazado al elemento actual
                2: De entro todas las preguntas a cargar seleccionamos una y guardamos su id
                3: Cargamos la pregunta
            """""

            group = QuestionsGroup.objects.get(element=element)

            questions = group.questions.all()

            number_of_questions = questions.count()

            random_question = random.randint(0, number_of_questions - 1)

            print("Random question: " + str(questions[random_question].statement))
            request.session['question_to_load_id'] = questions[random_question].id

            return HttpResponseRedirect(reverse('exam:load_question'))

        elif element.is_second_level_node:
            """""
                Este tipo de elemento tiene varias partes llamadas second level ways adheridas a él. A su vez, a cada
                una de estas partes hay conectados varios elementos que, en la primera versión, serán sólo preguntas.

                El funcionamiento es como sigue:

                1: Se cargan todos los caminos asociados al elemento
                2: Se selecciona uno de forma aleatoria
                3: Se guarda su id en slw_id
                4: load_slw se encargará de cargar todos los elementos asociados a él
            """""

            ways = SecondLevelWay.objects.filter(second_level_node=element)

            number_of_ways = ways.count()

            random_way = random.randint(0, number_of_ways - 1)

            request.session['slw_id'] = ways[random_way].id

            request.session['actual_slw_element'] = 0

            return HttpResponseRedirect(reverse('exam:load_slw'))
        elif element.is_topic_element:
            return HttpResponseRedirect(reverse('exam:load_topics'))

    else:
        # Cargamos la siguiente parte del examen
        request.session['actual_part'] += 1
        return HttpResponseRedirect(reverse('exam:load_part'))


def load_topics(request):
    topics = TopicElement.objects.get(element=request.session['actual_element_id']).topics.all()

    return render(request, 'exam/element_topics.html', {
        'exam': Exam.objects.get(pk=request.session['exam_id']),
        'call': Call.objects.get(pk=request.session['call_id']),
        'avatar': Avatar.objects.get(pk=request.session['avatar_id']),
        'part': Part.objects.get(pk=request.session['actual_part_id']),
        'element': Element.objects.get(pk=request.session['actual_element_id']),
        'progress': 15,
        'topics': topics,
        'student': User.objects.get(pk=request.session['student_id']),
    })


def load_topic_expressions(request, topic_id):
    topic = Topic.objects.get(pk=topic_id)

    # TODO Mejorar eficiencia en esta llamada
    # Problema de usar order_by('?') http://stackoverflow.com/questions/1731346/how-to-get-two-random-records-with-django
    expressions = TopicExpression.objects.filter(topic=topic).order_by('?')[:10]  # 10 random results.

    return render(request, 'exam/element_topic_expressions.html', {
        'exam': Exam.objects.get(pk=request.session['exam_id']),
        'call': Call.objects.get(pk=request.session['call_id']),
        'avatar': Avatar.objects.get(pk=request.session['avatar_id']),
        'part': Part.objects.get(pk=request.session['actual_part_id']),
        'element': Element.objects.get(pk=request.session['actual_element_id']),
        'progress': get_progress(request),
        'topic': topic,
        'expressions': expressions,
        'student': User.objects.get(pk=request.session['student_id']),
    })


def load_question(request):
    return render(request, 'exam/element_question.html', {
        'exam': Exam.objects.get(pk=request.session['exam_id']),
        'call': Call.objects.get(pk=request.session['call_id']),
        'avatar': Avatar.objects.get(pk=request.session['avatar_id']),
        'part': Part.objects.get(pk=request.session['actual_part_id']),
        'element': Element.objects.get(pk=request.session['actual_element_id']),
        'progress': 15,
        'question': Question.objects.get(pk=request.session['question_to_load_id']),
        'student': User.objects.get(pk=request.session['student_id']),
    })


# Idéntico al cargar pregunta sólo que al terminar carga load_slw en lugar de load_element
def load_slw_question(request):
    return render(request, 'exam/element_slw_question.html', {
        'exam': Exam.objects.get(pk=request.session['exam_id']),
        'call': Call.objects.get(pk=request.session['call_id']),
        'avatar': Avatar.objects.get(pk=request.session['avatar_id']),
        'part': Part.objects.get(pk=request.session['actual_part_id']),
        'element': Element.objects.get(pk=request.session['actual_element_id']),
        'progress': 15,
        'question': Question.objects.get(pk=request.session['question_to_load_id']),
        'student': User.objects.get(pk=request.session['student_id']),
    })


def load_slw(request):

    actual_slw_element = int(request.session['actual_slw_element'])

    slw = SecondLevelWay.objects.get(pk=request.session['slw_id'])

    # print("SLW: " + str(actual_slw_element) + " / " + str(Element.objects.filter(second_level_way=slw).count()))
    if actual_slw_element < Element.objects.filter(second_level_way=slw).count():

        # Elementos enlazados a esta slw
        slw_elements = Element.objects.filter(second_level_way=slw).order_by('order')

        # Guardamos la id del elemento a cargar (en el caso de las preguntas, el elemento enlazado a la misma)
        request.session['question_to_load_id'] = Question.objects.get(element=slw_elements[actual_slw_element]).id

        request.session['actual_slw_element'] += 1

        print("Cargando pregunta SLW: " + Question.objects.get(element=slw_elements[actual_slw_element]).statement)

        return HttpResponseRedirect(reverse('exam:load_slw_question'))
    else:
        return HttpResponseRedirect(reverse('exam:load_element'))


def the_end(request):
    return render(
        request, 'exam/the_end.html', {
            'progress': 100,
        }
    )



