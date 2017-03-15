from django.contrib import admin
from .models import *
# Register your models here.


class ElementInline(admin.StackedInline):
    model = Element
    extra = 1


class PartAdmin(admin.ModelAdmin):
    inlines = [ElementInline]


admin.site.register(Part, PartAdmin)
admin.site.register(Question)

admin.site.register(Topic)
admin.site.register(TopicExpression)
admin.site.register(TopicsChoice)

admin.site.register(QuestionsGroup)

admin.site.register(SecondLevelWay)

admin.site.register(TopicElement)

admin.site.register(Level)
admin.site.register(Element)
admin.site.register(AuxText)
admin.site.register(Voice)
admin.site.register(Avatar)
admin.site.register(Call)
admin.site.register(Exam)
admin.site.register(Center)
admin.site.register(Country)
