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

import redis
from redisconfig import *

import simplejson
from django.core.serializers import json

import time

import re

db = redis.Redis(REDIS_HOST, password=REDIS_PASSWORD,
		port=REDIS_PORT)

class Chart:
	template = '''
   chart = new Highcharts.Chart({
      chart: {
         renderTo: 'idSTATNAME',
         defaultSeriesType: 'spline',
         marginRight: 10,
         events: {
            load: function() {
               var series = this.series[0];
               setInterval(function() {
				   $.get(url='stats/STATNAME',
				   	function (data) {
						for (i = 0; i < data.length; ++i) {
			series.addPoint([data[i][0], data[i][1]], true, series.data.length > 20);
						}
					}
				   )
               }, TIMEOUT);
            }
         }
      },
      title: {
         text: 'MTITLE'
      },
      xAxis: {
         type: 'datetime',
         tickPixelInterval: 100
      },
      yAxis: {
         title: { text: 'YTITLE' },
		 plotLines: [{ value: 0, width: 1 }],
      },
      tooltip: {
         formatter: function() {
                   return '<b>'+ this.series.name +'</b><br/>'+
               Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+ 
               Highcharts.numberFormat(this.y, 2);
         }
      },
      legend: {
         enabled: false
      },
      exporting: {
         enabled: false
      },
	  series: [ { name: 'hit', data: [] } ]
   });
'''
	def __init__(self, title, statname, timeout = 1000):
		self.title = title
		self.statname = statname
		self.ytitle = 'hits'
		self.timeout = timeout
		self.minute = False

	def __str__(self):
		r = self.template
		r = r.replace('MTITLE', self.title)
		r = r.replace('YTITLE', self.ytitle)
		r = r.replace('STATNAME', self.statname)
		r = r.replace('TIMEOUT', str(self.timeout))
		return r

	def stats(self):
		r = []
		t = time.time() - (self.timeout / 1000)
		for i in range(0, self.timeout / 1000):
			gmtime = time.gmtime(t)
			if self.minute:
				dt = time.strftime('%y:%m:%d:%H:%M', gmtime)
			else:
				dt = time.strftime('%y:%m:%d:%H:%M:%S', gmtime)
			cnt = db.hget('stats.' + self.statname, dt)
			if not cnt:
				cnt = 0
			r.append([ int(t * 1000), cnt ])
			t += 1
		return r

class JsonResponse(HttpResponse):
	def __init__(self, object, callback):
		content = simplejson.dumps(
				object, indent=2, cls=json.DjangoJSONEncoder,
				ensure_ascii=False)
		if callback != None:
			content = callback + '(' + content + ')'
		super(JsonResponse, self).__init__(
				content, content_type='application/json')

charts = {};
def addChart(title, statname, timeout = 1000):
	charts[statname] = Chart(title, statname, timeout)

addChart('Training index hits',    'train.index')
addChart('Training sendtext hits', 'train.sendtext')
addChart('Wordcounter workers', 'wordcount')
addChart('Wordcounter worker1', 'wordcount.spell-worker1', 2000)
addChart('Wordcounter worker2', 'wordcount.spell-worker2', 2000)
addChart('Wordcounter worker3', 'wordcount.spell-worker3', 2000)
addChart('Words per minute', 'wordspermin', 4000)
addChart('Uniq words per minute', 'uniqwordspermin', 4000)

charts['wordspermin'].minute = True
charts['uniqwordspermin'].minute = True

def index(request):
	return render_to_response('monitor.html', { 'charts': charts.values() },
			context_instance = RequestContext(request))

def stats(request, stat):
	callback = request.GET.get('callback')
	return JsonResponse(charts[stat].stats(), callback)

class QueryFormRank(forms.Form):
	minRank = forms.IntegerField(min_value=0, initial=0)
	maxRank = forms.IntegerField(min_value=0, initial=42)

class QueryFormWords(forms.Form):
	words = forms.CharField()

def query(request):
	queryFormRank = QueryFormRank()
	queryFormWords = QueryFormWords()
	data = ''

	if request.method == 'POST':
		if 'minRank' in request.POST:
			queryFormRank = QueryFormRank(request.POST)
			if queryFormRank.is_valid():
				data = db.zrange('words',
						queryFormRank.cleaned_data['minRank'],
						queryFormRank.cleaned_data['maxRank'], withscores=True)
				data = ['<tr><td>%s</td><td>%d</td></tr>'%(d[0], -d[1]) for d in data]
				data = '<table border=1><tr><th>word</th><th>score</th></tr>' + ''.join(data) + '</table>'
		
		if 'words' in request.POST:
			queryFormWords = QueryFormWords(request.POST)

			if queryFormWords.is_valid():
				words = re.findall('[\w]+', queryFormWords.cleaned_data['words'].lower())
				data = '<table border=1><tr><th>word</th><th>score</th></tr>'
				for word in words:
					score = db.zscore('words', word)
					if score:
						data += '<tr><td>%s</td><td>%d</td></tr>'%(word, -score)
					else:
						data += '<tr><td>%s</td><td>N/A</td></tr>'%(word)
				data += '</table>'

	return render_to_response('query.html', {
		'data': data,
		'QueryFormRank': queryFormRank,
		'QueryFormWords': queryFormWords,
		}, context_instance = RequestContext(request))
