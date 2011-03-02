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

db = redis.Redis(REDIS_HOST, password=REDIS_PASSWORD,
			port=REDIS_PORT)

def train(words):
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
