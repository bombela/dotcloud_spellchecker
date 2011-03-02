#!/usr/bin/env python
# coding: utf-8
'''
File    : views.py
Author  : François-Xavier Bourlet
Contact : bombela@gmail.com
Date    : 2011 Mar 02

Description : 
'''

from django.shortcuts import render_to_response, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from celery.task.sets import TaskSet
from wordcounter import wordcount

import redis
from redisconfig import *

from django.core.serializers import json

db = redis.Redis(REDIS_HOST, password=REDIS_PASSWORD,
			port=REDIS_PORT)


class JsonResponse(HttpResponse):
	def __init__(self, object, callback):
		content = simplejson.dumps(
				object, indent=2, cls=json.DjangoJSONEncoder,
				ensure_ascii=False)
		if callback != None:
			content = callback + '(' + content + ')'
		super(JsonResponse, self).__init__(
				content, content_type='application/json')

class SubmitTextForm(forms.Form):
	upfile = forms.FileField(required=False)
	url    = forms.URLField(required=False)
	text   = forms.CharField(max_length=1024*16,
			widget=forms.Textarea, required=False)

	def clean(self):
		super(forms.Form, self).clean()

		if not (self.cleaned_data['upfile']
				or self.cleaned_data['url']
				or self.cleaned_data['text']):
			raise forms.ValidationError('Empty form!')

		f = self.cleaned_data['upfile']
		if f and f.content_type != 'text/plain':
			raise forms.ValidationError('Send only text file please...')
		return self.cleaned_data

def splitText(text):
	r = list()
	while len(text) > 1024*16:
		i = 4095
		while text[i] != ' ':
			i -= 1
		r.append(text[0:i])
		text = text[i:]
	r.append(text)
	return r

def index(request):
	form = SubmitTextForm()
	return render_to_response('train.html', { 'form': form },
			context_instance=RequestContext(request))

def sendtext(request):
	print "heeeeeeeee"
	return HttpResponse("bof")

def sendtext2(request):
	print "heeeeeeeee"
	return HttpResponse("bof " + str(request.POST))

	if request.method != 'POST' or not request.is_ajax():
		return HttpResponseRedirect('/')
	print "plop"

	form = SubmitTextForm(request.POST, request.FILES)
	if form.is_valid():
		upfile = form.cleaned_data['upfile']
		url = form.cleaned_data['url']
		text = form.cleaned_data['text']
		validated = True
		if upfile:
			job = TaskSet(tasks=[wordcount.subtask([text])
				for chunk in upfile.chunks() for text in splitText(chunk)])
			results = job.apply_async()
# store resultes in session...
			for r in results:
				print r
		elif url:
			pass
		elif text:
			pass
		else:
			validated = False

	callback = request.GET.get('callback')
	return JsonResponse("lolita", callback)
