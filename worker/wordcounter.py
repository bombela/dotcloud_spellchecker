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
from time import sleep
from socket import gethostname

@task
def wordcount(what='pasta', howlong=10):
    sleep(howlong)
    return '[wordcounter] I am %s and I cooked some %s for you!'%(gethostname(), what)
