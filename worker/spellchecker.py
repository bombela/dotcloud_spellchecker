#!/usr/bin/env python
# coding: utf-8
'''
File    : spellchecker.py
Author  : François-Xavier Bourlet
Contact : bombela@gmail.com
Date    : 2011 Mar 01

Description : Spellcheck a piece of text.
'''

from celery.task import task
from time import sleep
from socket import gethostname

@task
def spellcheck(what='pasta', howlong=10):
    sleep(howlong)
    return '[spellchecker] I am %s and I cooked some %s for you!'%(gethostname(), what)
