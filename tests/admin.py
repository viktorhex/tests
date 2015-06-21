from django.contrib import admin
from .models import TestPrototype, QuestionPrototype, AnswerPrototype, ImagePrototype
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class AnswerInline(admin.StackedInline):
	model = AnswerPrototype

class QuestionForm(ModelForm):
	class Meta:
		model = QuestionPrototype
	test_id = None
	def __init__(self, *args, **kwargs):
		super(QuestionForm, self).__init__(*args, **kwargs)
		if self.test_id:
			self.fields['test'].queryset = model.objects().filter(test=self.test_id)
class QuestionAdmin(admin.ModelAdmin):
	model = QuestionPrototype
	inlines = [AnswerInline]
	form = QuestionForm
	def add_view(self, request, form_url='', extra_context=None):
		form.test_id = 1 #здесь нужно получить id теста по запросу
		return super(QuestionAdmin, self).add_view(request, form_url, extra_context)


class TestAdmin(admin.ModelAdmin):
    model = TestPrototype
    def response_add(self, request, obj, post_url_continue=None):
    	return HttpResponseRedirect('../../questionprototype/add/')#здесь нужно передать в запрос obj.test

admin.site.register(QuestionPrototype, QuestionAdmin)
admin.site.register(TestPrototype, TestAdmin)