#!/usr/bin/env python
# coding: utf-8
'''
File    : train.py
Author  : François-Xavier Bourlet
Contact : bombela@gmail.com
Date    : 2011 Mar 02

Description : 
'''

from django.shortcuts import render_to_response

def index(request):
	return render_to_response('train.html')
