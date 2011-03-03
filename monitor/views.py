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
				  	  t = (((new Date()).getTime() / 1000) - 1) * 1000;
					  series.addPoint([t, data[1]], true, series.data.length > 20);
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
		self.timeout = str(timeout)

	def __str__(self):
		r = self.template
		r = r.replace('MTITLE', self.title)
		r = r.replace('YTITLE', self.ytitle)
		r = r.replace('STATNAME', self.statname)
		r = r.replace('TIMEOUT', self.timeout)
		return r

	def stats(self):
		t = time.time() - 1
		gmtime = time.gmtime(t)
		cnt = db.hget('stats.' + self.statname,
				time.strftime('%y:%m:%d:%H:%M:%S', gmtime))
		if not cnt:
			cnt = 0
		return ( int(t * 1000), cnt )

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
addChart('Wordcounter worker1', 'wordcount.worker1', 2000)
addChart('Wordcounter worker2', 'wordcount.worker2', 2000)
addChart('Wordcounter worker3', 'wordcount.worker3', 2000)

def index(request):
	return render_to_response('monitor.html', { 'charts': charts.values() },
			context_instance = RequestContext(request))

def stats(request, stat):
	print stat
	callback = request.GET.get('callback')
	return JsonResponse(charts[stat].stats(), callback)
