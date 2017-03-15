from django.db import models
from django.utils import timezone
import os
import base64

from user.models import StudentProfile as Student, TeacherProfile as Teacher, CenterAdminProfile as CenterAdmin
from django.db.models.fields.files import ImageFile



# Centro de estudios
class Center(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nombre de la universidad, academia, etc
    name = models.CharField(max_length=100, unique=True, blank=False)

    # Las siglas del centro
    code = models.CharField(max_length=5, unique=True, blank=False)
    description = models.CharField(max_length=400, blank=False)
    address = models.CharField(max_length=200, blank=False)

    # Logo oficial de la escuela. Podrá aparecer en el perfil y en los exámenes
    logo = models.ImageField(upload_to=os.path.join('images/centers/logos'), blank=True)

    # Los profesores que colaboran con este centro
    teachers = models.ManyToManyField(Teacher, blank=True)

    # Un administrador de centro podrá crear exámenes, añadir profesores etc
    admins = models.ManyToManyField(CenterAdmin, blank=True)

    # Se guarda un registro de los alumnos que hacen exámenes pertenecientes al centro
    students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name


# Los paises disponibles para la internacionalización del examen
class Country(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=64, null=False)
    flag = models.ImageField(upload_to='images/languages/flags')

    def __str__(self):
        return self.name


# Las distintas voces con las que se podrá dictar un examen
class Voice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # El género de la voz
    VOICE_GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    voice_gender = models.CharField(max_length=1, choices=VOICE_GENDER)

    language = models.ForeignKey(Country, null=False)

    # El código varía en función de si es hombre o mujer
    js_code = models.CharField(max_length=128, null=False)

    def __str__(self):
        return str(self.language) + " (" + str(self.voice_gender) + ", " + str(self.js_code) + ")"


class Avatar(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nombre del personaje
    name = models.CharField(max_length=64, null=False)

    # Una breve biografía, ficticia o no del avatar
    description = models.CharField(max_length=128, null=False)

    # Necesario Pillow 2.9.o http://stackoverflow.com/questions/24646305/error-for-pip-install-pillow-on-ubuntu-virtualenv
    # Esta no es la imagen que se mostrará al usuario, sólo la que servirá para
    # image = models.ImageField(upload_to=os.path.join('exam/static/img/avatars'))
    image = models.ImageField(upload_to='images/exams/avatars')

    # Deberá tener el mismo nombre que la imagen de muestra
    svg_url = models.TextField(blank=True)

    # La voz que tendrá este avatar
    voice = models.ForeignKey(Voice, on_delete=models.CASCADE, unique=False)
    
    def __str__(self):
        return str(self.name) + " (" + str(self.voice.js_code) + ")"


# Los distintos niveles que permite evaluar la app: B1, C2 etc
class Level(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nombre del nivel
    name = models.CharField(max_length=64)

    # Certificado por el centro que sea (campo opcional)
    certified_by = models.ForeignKey(Center, null=True, blank=True)

    def __str__(self):
        if self.certified_by:
            return self.name + " (" + self.certified_by.name + ")"
        else:
            return self.name


# Clase que auna al resto de elementos esesnciales del sistema
class Exam(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nivel que, una vez superado el examen habrá logrado el alumno
    level = models.ForeignKey(Level, null=True)

    # Notas mínimas y máximas estipuladas para pasar el examen (y lograr el título) sobre 100
    min_mark = models.IntegerField(null=True)

    # Quien gestiona el examen
    responsible_teacher = models.ForeignKey(Teacher, blank=True, related_name='responsible', on_delete=models.CASCADE)
    created_by_center = models.ForeignKey(Center, related_name='creator', on_delete=models.CASCADE)

    # Centros en los que se puede realizar el examen (cada centro podrá controlar las convocatorias)
    allowed_centers = models.ManyToManyField(Center)

    # Nombre que aparecerá como título en todas las convocatorias
    name = models.CharField(max_length=128, blank=False)
    description = models.CharField(max_length=248)

    # Tiempos recomendados para hacer el examen
    max_time = models.IntegerField(default=30000)
    recommended_time = models.IntegerField(default=30000)

    welcome_message = models.TextField(blank=False, null=False)
    welcome_help = models.TextField(blank=True, null=True)

    # Voces disponibles para realizar el examen
    voices = models.ManyToManyField(Voice)

    def __str__(self):
        return self.name + " managed by " + str(self.responsible_teacher) + ". Belongs to " + str(self.created_by_center) + "."


# Una convocatoria no es más que un llamamiento a un examen ya configurado
class Call(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Rango de tiempo en que la convocatoria estará abierta
    starts_at = models.DateTimeField(blank=False)
    ends_at = models.DateTimeField(blank=False)

    # Se podrá desactivar una convocatoria, y será imposible acceder a ella
    # TODO Echar a los alumnos que estén haciendo el examen si se desactiva?
    active = models.BooleanField(default=True)

    # El examen al que pertenece la convocatoria
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    # Un nombre que describa la convocatoria, o la justifique
    name = models.CharField(max_length=128, blank=False)

    # La pass para acceder a la convocatoria. Ha de ser única.
    # TODO Cifrar la contraseña
    password = models.CharField(max_length=64, blank=False, unique=True)

    # Los profesores con acceso a la corrección de la convocatoria
    examinators = models.ManyToManyField(Teacher, blank=True)

    # print today.strftime('We are the %d, %b %Y') 'We are the 22, Nov 2008'
    def __str__(self):
        return self.name + ". Opened from " + str(self.starts_at) + " to " + str(self.ends_at) + "."


# Un simple fragmento de texto auxiliar que permite añadir opciones necesarias en el contexto de la app
# SE USARÁ SÓLO PARA FUNCIONES NO CRÍTICAS, ES DECIR, POR EJEMPLO NO PARA ALMACENAR LAS PREGUNTAS
# O LOS TÍTULOS
class AuxText(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Indica si el texto ha de ser o no dictado
    dictate = models.BooleanField(default=False)

    # Indica si se imprime en pantalla
    print_it = models.BooleanField(default=True)
    # Si irá entre etiquetas h1 o no
    #is_title = models.BooleanField(default=False)

    # El texto básico
    text = models.TextField()

    def __str__(self):
        return self.text

# TODO Añadir clase estilo AuxText pero sólo de comandos de voz


# Cada Parte de las que está compuesta el examen
class Part(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # El examen al que pertenece esta parte
    exam = models.ForeignKey(Exam)

    # Orden de esta parte del examen
    order = models.IntegerField()

    # El título de la parte del examen que sea. Se decide si se dicta o no en AuxText
    title = models.TextField()
    print_title = models.BooleanField(default=True)
    dictate_title = models.BooleanField(default=False)

    # Una introducción de la parte del examen que se muestra en la portada de la portada
    introduction = models.CharField(max_length=2048)
    print_introduction = models.BooleanField(default=True)
    dictate_introduction = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# De una división de caminos pueden surgir varias partes.
# Cada parte deberá estar enlazada AL MISMO ELEMENTO de tipo is_elements_diversion
# Se seleccionará una delas partes enlazada almismo elemento de forma aleatoria
# A cada parte se enlazará cada elemento de esa parte secundaria
class SecondLevelWay(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Todas los posibles caminos que partan del elemento que hace la división apuntarán al mismo
    second_level_node = models.ForeignKey('Element')
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


# El examen está formado por elementos que pueden ser preguntas, grupos de preguntas etc
class Element(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Parte del examen al que pertenece el elemento
    # ENLAZAR SÓLO SI NO ES UN ELEMENTO DE NIVEL 2
    part = models.ForeignKey(Part, null=True, blank=True)

    # En el caso de que este element sea hijo de segundo nivel, el camino padre
    second_level_way = models.ForeignKey(SecondLevelWay, null=True, blank=True)

    # Orden dentro de esta parte del examen
    # Necesario también en los diversion
    order = models.IntegerField()

    # Determinación del tipo de elemento mediante booleanos
    is_question = models.BooleanField(default=False)
    is_questions_group = models.BooleanField(default=False)
    is_second_level_node = models.BooleanField(default=False)
    is_topic_element = models.BooleanField(default=False)

    def __str__(self):
        if self.is_question:
            tipo = "Question"
        elif self.is_questions_group:
            tipo = "Questions group"
        elif self.is_second_level_node:
            tipo = "Second level node"
        elif self.is_topic_element:
            tipo = "Topic element"
        else:
            tipo = "Elemento sin identificar"

        # Hacemos la cuenta para el primer nivel o para el segundo
        if self.part:
            belongs_to = "part " + str(self.part.title)
            total_part = Element.objects.filter(part=self.part).count()
        elif self.second_level_way:
            belongs_to = str(self.second_level_way.name) + " second level way"
            total_part = Element.objects.filter(second_level_way=self.second_level_way).count()
        else:
            belongs_to = " an unknow path/way/part "
            total_part = 0
        # Examen - Orden del elemento - Tipo de elemento
        return tipo + " element that belongs to the '" + belongs_to + "', where occupies the position " + str(self.order) + "/" + str(total_part)


# Módulo de pregunta simple
class Question(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # Elemento referenciado.
    # Puede ser nulo en el caso de que la pregunta pertenezca a un grupo
    element = models.ForeignKey(Element, null=True, blank=True)

    # Enunciados principal y de backup
    statement = models.TextField()
    dictate_statement = models.BooleanField(default=True)
    print_statement = models.BooleanField(default=True)

    # Veces que se podra escuchar el enunciado
    attempts_statement = models.IntegerField(default=1, blank=True, null=True)

    # Enunciado de respaldo. Hereda las cualidades de el enunciado padre
    statement_backup = models.TextField(blank=True, null=True)



    # Tiempo para lanzar el backup
    time_to_backup = models.IntegerField(default=10)
    allow_backup_buttton = models.BooleanField(default=True)

    # TODO Añadir campo en el que se pueda introducir el comando, o hacer uno universal
    allow_backup_voice = models.BooleanField(default=False)

    # Tiempo que el estudiante tendrá para responder, en segundos
    time_to_respond = models.IntegerField(default=10)

    # Tiempo mínimo de respuesta. Si el usuario responde con una respuesta menor, se le podrá
    # permitir repetir la pregunta (en función del número de attemps restantes)
    min_time = models.IntegerField(default=1)

    # Veces que se permitirá responder la pregunta. Se guardará la última pregunta
    attemps_response = models.IntegerField(default=1)

    # Botón que permitirá repetir la pregunta
    allow_repeat_button = models.BooleanField(default=False)
    allow_repeat_voice = models.BooleanField(default=False)

    # Fragmentos de texto antes y después de la pregunta. Se pueden configurar para que sean dictados por el ordenador
    pre_statement = models.CharField(max_length=2048, blank=True, null=True)
    post_statement = models.CharField(max_length=2048, blank=True, null=True)

    # Este es un trozo de texto que se ejecutará sólo cuando el usuario haya terminado de responder
    post_answer = models.CharField(max_length=2048, blank=True, null=True)

    def __str__(self):
        return self.statement


# Un simple grupo de preguntas
class QuestionsGroup(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    element = models.ForeignKey(Element, null=True, blank=True)

    # Identificador legible por humanos que describa el grupo
    name = models.CharField(max_length=100)
    
    # Las preguntas del grupo
    questions = models.ManyToManyField(Question)

    # Si queremos seleccionar o no de forma aleatoria
    # random_select = models.BooleanField(default=False)

    # Número de preguntas que se mostrarán de forma aleatoria si random_select == True
    # random_number = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# Se puede enganchar un mecanismo completo de selección de tópicos a un elemento para integrarlo en una parte del examen
class TopicElement(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    element = models.ForeignKey(Element)
    topics = models.ManyToManyField('Topic')

    def __str__(self):
        return "Topics group"

class Topic(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class TopicExpression(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    topic = models.ForeignKey(Topic)

    expression = models.CharField(max_length=512)

    def __str__(self):
        return self.expression + " (" + self.topic.name + ")"


# Muestra unos cuántos tópicos y permite que el usuario los seleccione
class TopicsChoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    element = models.ForeignKey(Element)

    topics = models.ManyToManyField(Topic)

    time_to_choose = models.IntegerField(default=30)

    # time_to_respond =


# Habrá una sesión por cada usuario que realice la convocatoria
class Session(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Se liga a una convocatoria
    call = models.ForeignKey(Call, on_delete=models.CASCADE)

    # Enlazamos también a un estudiante
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)

    # Guardamos la ip de la conexión
    ip = models.CharField(max_length=12, blank=True, default="1.1.1.1")

    # Guardamos el avatar que el estudiante haya escogido
    avatar = models.ForeignKey(Avatar, blank=True, null=True)

    # TODO Guardar la mac del equipo

    def __str__(self):
        return self.student + " session at " + self.call + " call."