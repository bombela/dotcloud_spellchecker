#!/usr/bin/env python
# coding: utf-8
'''
File    : wordcounter.py
Author  : François-Xavier Bourlet
Contact : bombela@gmail.com
Date    : 2011 Mar 01

Description : Count word occurences in some text.
'''

from celery.task import task
from socket import gethostname
import re
import redis
from redisconfig import *
import time

def train(words):
	db = redis.Redis(REDIS_HOST, password=REDIS_PASSWORD,
				port=REDIS_PORT)
	
	gmtime = time.gmtime()
	dt = time.strftime('%y:%m:%d:%H:%M:%S', gmtime)

	db.hincrby('stats.wordcount', dt, 1);
	db.hincrby('stats.wordcount.' + gethostname(), dt, 1);

	stats = set()
	pipe = db.pipeline(transaction=True)
	for w in words:
		pipe.zincrby('words', w, -1)
		stats.add(w)
	pipe.execute()
	return len(stats)

@task
def wordcount(text):
	cnt = train(re.findall('[\w]+', text.lower()))
	return '[wordcounter on %s] %d words' %(gethostname(), cnt)

if __name__ == "__main__":
	print wordcount("hello pouet titi titi pouet pouet")
