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

def redisDb(dbname):
	return redis.Redis(REDIS_HOST, password=REDIS_PASSWORD,
			port=REDIS_PORT, db=dbname)

db_words = redisDb('words')

def train(words):
	for w in words:
		db_words.incr(w)

@task
def wordcount(text):
	cnt = 42
	train(re.findall('[\w]+', text.lower()))
	return '[wordcounter on %s] %d words'%(gethostname(), cnt)

if __name__ == "__main__":
	print wordcount("hello pouet titi")
