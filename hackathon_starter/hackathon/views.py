#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Django
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.urlresolvers import reverse
import time
import requests
from django.db import connection
import os
from django.conf import settings
import base64
from collections import OrderedDict
from urllib import urlopen
from time import gmtime, strftime

# Django REST Framework
from rest_framework import viewsets, mixins

# Python
import oauth2 as oauth
import simplejson as json
import requests

# Models
from hackathon.models import *
from hackathon.serializers import SnippetSerializer
from hackathon.forms import UserForm

import pyrebase
from firebase_token_generator import create_token
import json
from twilio.rest import TwilioRestClient

config = {
  "apiKey": "AIzaSyBA1QJqobSlNn3PZ8fSNx0BHqqYGsACtsU",
  "authDomain": "baytreeexpress-53112.firebaseapp.com",
  "databaseURL": "https://baytreeexpress-53112.firebaseio.com",
  "storageBucket": "baytreeexpress-53112.appspot.com",
  "messagingSenderId": "70657304005",
}

def index(request):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    indicas = []
    sativas = []
    hybrids = []

    nugs = db.child("indica").get()
    for nug in nugs.each():
        indicas.append({'name' : str(nug.key()).replace("_"," ") , 'gram' : nug.val() , 'img' :  str(nug.key()) })

    nugs = db.child("hybrid").get()
    for nug in nugs.each():
        hybrids.append({'name' : str(nug.key()).replace("_"," ") , 'gram' : nug.val() , 'img' :  str(nug.key())  })


    nugs = db.child("sativa").get()
    for nug in nugs.each():
        sativas.append({'name' : str(nug.key()).replace("_"," ") , 'gram' : nug.val() , 'img' :  str(nug.key())  })

    context = {}
    context['indicas'] = indicas
    context['hybrids'] = hybrids
    context['sativas'] = sativas
    return render(request, 'hackathon/index.html', context)

@csrf_exempt
def register(request):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    db = firebase.database()
    try:
        auth.create_user_with_email_and_password(str(request.POST['email']),str(request.POST['password']))
        user = auth.sign_in_with_email_and_password(str(request.POST['email']),str(request.POST['password']))
        token = user['idToken']
        data = {}
        data['user'] = str(request.POST['email'])
        results = db.child("users").push(data, token)
        return JsonResponse({'user':str(request.POST['email']) , 'token' : token, 'error': 'none' })
    except:
        return JsonResponse({'user': '', 'token' : '', 'error': 'error' })

@csrf_exempt
def login(request):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    db = firebase.database()
    try:
        print(str(request.POST['email']))
        print(str(request.POST['password']))
        user = auth.sign_in_with_email_and_password(str(request.POST['email']),str(request.POST['password']))
        # user = auth.refresh(user['refreshToken'])
        token = user['idToken']
        print(token)
        data = {
          "user" : str(request.POST['email']),
          "date" : str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        }
        results = db.child("users").push(data, token)
        return JsonResponse({'user':str(request.POST['email']) , 'token' : token, 'error': 'none' })
    except:
        return JsonResponse({'user': '', 'token' : '', 'error': 'error' })

@csrf_exempt
def upload(request):
    print(request.FILES['file'])
    user = str(request.POST['user'])
    print(user)
    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    storage.child("images/"+str(user)+"/"+str(request.FILES['file'])).put(request.FILES['file'])
    ACCOUNT_SID = 'ACff521c563713463e8ba30b7bfe178765'
    AUTH_TOKEN = '05c27626b84c5440b4a2f81acf0d4d3b'

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    text_string = "You have a new user to verify. Login to Firebase and verify the email: " + str(request.POST['user'])
    client.messages.create(
        to = '+4156508944',
        from_ = '+17042009330',
        body = text_string,
    )  
    return JsonResponse({'action':'completed'})


@csrf_exempt
def submit_order(request):
  try:
    cart = json.loads(str(request.POST['cart']))
    address = str(request.POST['address'])
    text_string = "New Order! Deliver to " + str(address) + " \n"
    count = 1
    total = 0
    for item in cart:
      total += int(item['price'])
      add_string = str(count) + ". " + str(item['strain']) + " - " + str(item['qty']) + " ( $" + str(item['price']) + " ) \n"
      text_string += add_string
      count += 1
    text_string += " TOTAL PRICE : $" + str(total) + " \n"
    text_string += " TIME OF ORDER : " + str(strftime("%m/%d %H:%M", gmtime()))
    ACCOUNT_SID = 'ACff521c563713463e8ba30b7bfe178765'
    AUTH_TOKEN = '05c27626b84c5440b4a2f81acf0d4d3b'

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        to = '+4156508944',
        from_ = '+17042009330',
        body = text_string,
    )
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    db.child("orders").push(text_string, request.POST['token'] )
    return JsonResponse({'action':'complete'})
  except:
    return JsonResponse({'action':'error'})
    





