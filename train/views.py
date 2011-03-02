#!/usr/bin/env python
# coding: utf-8
'''
File    : views.py
Author  : François-Xavier Bourlet
Contact : bombela@gmail.com
Date    : 2011 Mar 02

Description : 
'''

from django.shortcuts import render_to_response
from celery.execute import send_task
import redis
from redisconfig import *

db = redis.Redis(REDIS_HOST, password=REDIS_PASSWORD,
			port=REDIS_PORT)

def wordcount_job(text):
	return send_task("wordcounter.wordcount", args=[text])

def index(request):
	return render_to_response('train.html')
