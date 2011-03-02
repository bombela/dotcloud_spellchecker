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

import simplejson
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

	def _check(self, name):
		r = name in self.cleaned_data and self.cleaned_data[name]
		if r:
			return 1
		return 0

	def clean(self):
		super(forms.Form, self).clean()

		used = 0
		used += self._check('upfile')
		used += self._check('url')
		used += self._check('text')
		if used == 0:
			raise forms.ValidationError('Empty form!')
		if used != 1:
			raise forms.ValidationError('Pick one field!')

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
	if request.method != 'POST':
		return HttpResponseRedirect('/')
	
	callback = request.GET.get('callback')
	form = SubmitTextForm(request.POST, request.FILES)
	
	if not form.is_valid():
		return JsonResponse({
			'form': form.as_p()
			}, callback)

	upfile = form.cleaned_data['upfile']
	url = form.cleaned_data['url']
	text = form.cleaned_data['text']
	if upfile:
		job = TaskSet(tasks=[wordcount.subtask([text])
			for chunk in upfile.chunks() for text in splitText(chunk)])
# store resultes in session...
	elif url:
# download file
		pass
	elif text:
		job = TaskSet(tasks=[wordcount.subtask([t]) for t in splitText(text)])
		pass
	
	results = job.apply_async()

	if request.is_ajax() or ('ajax' in request.POST):
		response = (0, results.total)
	else:
		response = [r for r in results]

	return JsonResponse({
		'form': form.as_p(),
		'response': response
		}, callback)
