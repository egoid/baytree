# Django
from django.shortcuts import render
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

# Django REST Framework
from rest_framework import viewsets, mixins

# Scripts
from scripts.steam import gamespulling, steamidpulling
from scripts.github import *
from scripts.tumblr import TumblrOauthClient
from scripts.twilioapi import *
from scripts.instagram import *
from scripts.scraper import steamDiscounts
from scripts.quandl import *
from scripts.twitter import TwitterOauthClient
from scripts.nytimes import *
from scripts.meetup import *
from scripts.linkedin import LinkedinOauthClient
from scripts.yelp import requestData
from scripts.facebook import *
from scripts.googlePlus import *
from scripts.dropbox import *
from scripts.foursquare import *

# Python
import oauth2 as oauth
import simplejson as json
import requests

# Models
from hackathon.models import *
from hackathon.serializers import SnippetSerializer
from hackathon.forms import UserForm


profile_track = None
getTumblr = TumblrOauthClient(settings.TUMBLR_CONSUMER_KEY, settings.TUMBLR_CONSUMER_SECRET)
getInstagram = InstagramOauthClient(settings.INSTAGRAM_CLIENT_ID, settings.INSTAGRAM_CLIENT_SECRET)
getTwitter = TwitterOauthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
getGithub = GithubOauthClient('2a11ce63ea7952d21f02', '7e20f82a34698fb33fc837186e96b12aaca2618d')
getLinkedIn = LinkedinOauthClient(settings.LINKEDIN_CLIENT_ID, settings.LINKEDIN_CLIENT_SECRET)
getFacebook = FacebookOauthClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
getGoogle = GooglePlus(settings.GOOGLE_PLUS_APP_ID, settings.GOOGLE_PLUS_APP_SECRET)
getDropbox = DropboxOauthClient(settings.DROPBOX_APP_ID, settings.DROPBOX_APP_SECRET)
getFoursquare = FoursquareOauthClient(settings.FOURSQUARE_APP_ID, settings.FOURSQUARE_APP_SECRET)

import pyrebase

def index(request):

    config = {
      "apiKey": "AIzaSyBA1QJqobSlNn3PZ8fSNx0BHqqYGsACtsU",
      "authDomain": "baytreeexpress-53112.firebaseapp.com",
      "databaseURL": "https://baytreeexpress-53112.firebaseio.com",
      "storageBucket": "",
      "messagingSenderId": "70657304005",
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    indicas = []
    sativas = []
    hybrids = []

    nugs = db.child("indica").get()
    for nug in nugs.each():
        indicas.append({'name' : str(nug.key()).replace("_"," ") , 'gram' : nug.val() })

    nugs = db.child("hybrid").get()
    for nug in nugs.each():
        hybrids.append({'name' : str(nug.key()).replace("_"," ") , 'gram' : nug.val() })


    nugs = db.child("sativa").get()
    for nug in nugs.each():
        sativas.append({'name' : str(nug.key()).replace("_"," ") , 'gram' : nug.val() })

    context = {}
    context['indicas'] = indicas
    context['hybrids'] = hybrids
    context['sativas'] = sativas
    return render(request, 'hackathon/index.html', context)


##################
#  API Examples  #
##################

def api_examples(request):
    context = {'title': 'API Examples Page'}
    return render(request, 'hackathon/api_examples.html', context)

#################
#   STEAM API   #
#################

def steam(request):
    key = '231E98D442E52B87110816C3D5114A1D'
    SteamUN = "Marorin"
    steamID = steamidpulling(SteamUN, key)
    game = gamespulling(steamID, key)
    return render(request,'hackathon/steam.html', {"game": game })

def steamDiscountedGames(request):
    data = steamDiscounts()
    return JsonResponse({ 'data': data })

#################
#  FACEBOOK API #
#################

def facebook(request):
    '''
    This is an example of getting basic user info and display it
    '''
    userInfo = getFacebook.get_user_info()
    return render(request, 'hackathon/facebookAPIExample.html', { 'userInfo' : userInfo})

#################
#  GOOGLE API   #
#################
def googlePlus(request):

    userInfo = getGoogle.get_user_info()
    return render(request, 'hackathon/googlePlus.html', {'userInfo' : userInfo})

#################
#  DROPBOX API  #
#################
def dropbox(request):
    userInfo = getDropbox.get_user_info()
    return render(request, 'hackathon/dropbox.html', {'userInfo' : userInfo})

def dropboxSearchFile(request):
    if request.method == 'POST':
        SEARCH_FILE_URL = 'https://api.dropbox.com/1/search/auto/'
        requestParams = {'query': request.POST['filename'],
                         'file_limit': '1000',
                         'include_deleted': True,
                         'access_token': getDropbox.access_token}
        response = requests.post(SEARCH_FILE_URL, data=requestParams)

        if response.status_code!=200:
            raise(Exception('Invalid response, response code {c}'.format(c=response.status_code)))

        return render(request, 'hackathon/dropboxSearchFile.html', {'data': response.json()})

#######################
#    FOURSQUARE API   #
#######################

def foursquare(request):
    userInfo = getFoursquare.get_user_info()
    return render(request, 'hackathon/foursquare.html', {'data' : userInfo})


#################
#    YELP API   #
#################

def yelp(request):
    data = {}
    if request.method == 'POST':
        location = request.POST.get('location')
        data = requestData(location)
    return render(request, 'hackathon/yelp.html', { 'data': data })

#################
#   MEETUP API  #
#################

def meetup(request):
    REDIRECT_URI = 'http://127.0.0.1:8000/hackathon/meetupToken'
    AUTHORIZE_URL = 'https://secure.meetup.com/oauth2/authorize?client_id=' + settings.MEETUP_CONSUMER_KEY + '&response_type=code' + '&redirect_uri=' + REDIRECT_URI
    return HttpResponseRedirect(AUTHORIZE_URL)

def meetupToken(request):
    access_token_url = 'https://secure.meetup.com/oauth2/access?'
    REDIRECT_URI = 'http://127.0.0.1:8000/hackathon/meetupToken'
    url = access_token_url + 'client_id=' +  settings.MEETUP_CONSUMER_KEY + '&client_secret=' + settings.MEETUP_CONSUMER_SECRET + '&grant_type=authorization_code' + '&redirect_uri=' + REDIRECT_URI + '&code=' +  request.GET.get('code')

    response = requests.post(url)
    access_token = json.loads(response.content)['access_token']
 
    if not MeetupToken.objects.all().exists():
        meetupToken = MeetupToken(access_token = access_token)
        meetupToken.save()
    else:
        meetupToken = MeetupToken(access_token = access_token)
        MeetupToken.objects.all()[0] = meetupToken
    return HttpResponseRedirect('http://127.0.0.1:8000/hackathon/meetupUser/')

def meetupUser(request):
    if not MeetupToken.objects.all().exists():
        return HttpResponseRedirect('http://127.0.0.1:8000/hackathon/meetup')
    access_token = MeetupToken.objects.all()[0]
    meetupData = {}
    userData = retrieveUserData('https://api.meetup.com/2/member/self/?access_token=' + str(access_token))
    meetupData['userData'] = userData
    return render(request, 'hackathon/meetup.html', { 'data': meetupData })

#################
#   QUANDL API  #
#################

def quandlDowJones(request):
    '''Returns JSON response about the latest dowjones index.'''
    dowjonesdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    print dowjonesdata
    return JsonResponse({'data': dowjonesdata})

def quandlSnp500(request):
    '''Returns JSON response about the latest SNP 500 index.'''
    snpdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    return JsonResponse({'data': snpdata})

def quandlNasdaq(request):
    '''Returns JSON response about the latest nasdaq index.'''
    nasdaqdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    return JsonResponse({'data': nasdaqdata})

def quandlapple(request):
    '''Returns JSON response about the latest apple stock.'''
    appledata = fetchstockData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    return JsonResponse({'data': appledata})

def quandlNasdaqdiff(request):
    '''Returns JSON response about the latest nasdaq index.'''
    nasdaqdata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    return JsonResponse({'data': nasdaqdata})

def quandlSnp500diff(request):
    '''Returns JSON response about the latest SNP 500 index.'''
    snpdata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    return JsonResponse({'data': snpdata})

def quandlDowJonesdiff(request):
    '''Returns JSON response about the latest dowjones index.'''
    dowjonesdata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    return JsonResponse({'data': dowjonesdata})

def quandlapplediff(request):
    '''Returns JSON response about the latest apple stock.'''
    appledata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    return JsonResponse({'data': appledata})

def quandlstocks(request):
    everyData = {}
    dowjonesdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    everyData['dow'] = dowjonesdata
    everyData['dowdiff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    snpdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    everyData['snp'] = snpdata
    everyData['snpdiff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    nasdaqdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    everyData['nasdaq'] = nasdaqdata
    everyData['nasdaqdiff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    everyData['apple'] = fetchstockData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    everyData['applediff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    return render(request, 'hackathon/quandl.html', { 'everyData': everyData })

#################
#  NYTIMES API  #
#################

def nytimespop(request):
    '''Returns JSON response about the most viewed articles for the last 24 hours.'''
    popdata = fetcharticle(settings.POPAPIKEY, 'http://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json?')
    return JSONResponse({'data': popdata})

def nytimestop(request):
    '''Returns JSON response about the articles located in the homepage'''
    topdata = fetcharticle(settings.TOPAPIKEY, 'http://api.nytimes.com/svc/topstories/v1/home.json?')
    return JSONResponse({'data': topdata})

def nytimesarticles(request):
    everyData = {}
    popdata = fetcharticle(settings.POPAPIKEY, 'http://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json?')
    topdata = topdata = fetcharticle(settings.TOPAPIKEY, 'http://api.nytimes.com/svc/topstories/v1/home.json?')
    everyData['top'] = topdata
    everyData['pop'] = popdata
    return render(request, 'hackathon/nytimes.html', { 'everyData': everyData })

#################
#   GITHUB API  #
#################

def githubUser(request):
    '''Returns Github Profile data for a specific user.'''
    parsedData = {}
    if request.method == 'POST':
        user = request.POST.get('user')
        parsedData['userData'] = getUserData(user, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    return render(request, 'hackathon/github.html', {'data': parsedData})

def githubTopRepositories(request):
    '''Returns Top Commited Repositories for a specific Github User'''

    parsedData = {}
    if request.method == 'POST':
        user = request.POST.get('user')
        repositories = getUserRepositories(user, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
        list = getTopContributedRepositories(user, repositories, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
        filtered = filterCommits(list)
        parsedData['committed'] = filtered
        print parsedData
    return render(request, 'hackathon/githubTopRepositories.html', {'data': parsedData})

def githubResume(request):
    '''A sample application which pulls various Github data to form a Resume of sorts'''

    allData = {}
    userData = getUserData('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    repositories = getUserRepositories('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    list = getTopContributedRepositories('DrkSephy', repositories, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    filtered = filterCommits(list)
    stargazers = getStarGazerCount('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    filteredStargazers = filterStarGazerCount(stargazers)
    forkedRepos = getForkedRepositories('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    allData['userData'] = userData
    allData['filteredData'] = filtered
    allData['filteredStargazers'] = filteredStargazers
    allData['forkedRepos'] = forkedRepos
    return render(request, 'hackathon/githubResume.html', { 'data': allData })


#################
#   TUMBLR API  #
#################

def tumblr(request):
    ''' Tumblr api calls '''
    if getTumblr.is_authorized:
        #get blogger twitterthecomic's blog information
        blog = getTumblr.getBlogInfo('twitterthecomic')
        #get tags that was tagged along starbucks
        tagged_blog = getTumblr.getTaggedInfo("starbucks")
        #get blog information tagged with starbucks
        blogontag = getTumblr.getTaggedBlog("starbucks")
    else:
        blog, tagged_blog, blogontag = '', '',''
        global profile_track
        profile_track = 'tumblr'
        tumblr_url = getTumblr.authorize_url()
        return HttpResponseRedirect(tumblr_url)

    context = {'title': "What's up Starbucks?", 'blogData': blog, 'blogTag': tagged_blog, 'blogontag': blogontag}
    return render(request, 'hackathon/tumblr.html', context)


####################
#   INSTAGRAM API  #
####################

def instagram(request):
    print getInstagram.is_authorized

    if getInstagram.is_authorized:
        if request.method == 'GET':
            if request.GET.items():
                instagram_tag = request.GET.get('instagram_tag')
                instagramUser = InstagramProfile.objects.get(user = request.user)
                tagged_media = getTaggedMedia(instagram_tag, instagramUser.access_token)
            else:
                instagram_tag, tagged_media = '', ''
    else:
        global profile_track
        profile_track = 'instagram'
        instagram_url =getInstagram.get_authorize_url()
        return HttpResponseRedirect(instagram_url)

    context = {'title': 'Instagram', 'tagged_media': tagged_media, 'search_tag': instagram_tag}
    return render(request, 'hackathon/instagram.html', context)

def instagramUser(request):
    ''' Returns JSON response about a specific Instagram User. '''

    access_token = InstagramProfile.objects.get(instagram_user='mk200789').access_token
    parsedData = getUserInfo(access_token)
    return JsonResponse({ 'data': parsedData })

def instagramUserMedia(request):
    ''' Returns JSON response about a specific Instagram User's Media. '''

    access_token = InstagramProfile.objects.get(instagram_user='mk200789').access_token
    parsedData = getUserMedia(32833691, access_token)
    return JsonResponse({'data': parsedData })

def instagramMediaByLocation(request):
    print request.user
    if request.method == 'GET':
        if request.GET.items():
            #check if user has a User profile
            if request.user in User.objects.all():
                #check if user has an Instagram profile
                user = User.objects.get(username=request.user)
                #if user has an Instagram profile, query the search
                if InstagramProfile.objects.all().filter(user=user.id):
                    address = request.GET.get('address_field')
                    access_token = InstagramProfile.objects.get(user=user.id).access_token
                    geocode_result = searchForLocation(address)
                    if geocode_result:
                        location_ids = searchLocationIds(geocode_result['lat'], geocode_result['lng'], access_token)
                        media = searchLocationMedia(location_ids, access_token)
                        title = address
                        err_msg = ''
                else:
                    title, media, err_msg, location_ids, geocode_result = 'Media by location','', str(request.user)+ ' does not have an InstagramProfile','', ''
        else:
            title, media, err_msg, location_ids, geocode_result = 'Media by location', '','', '', ''


    context = {'title': title, 'geocode_result':geocode_result, 'media':media, 'list_id':location_ids, 'err_msg': err_msg}
    return render(request, 'hackathon/instagram_q.html', context)


####################
#   TWITTER API    #
####################

def twitter(request):
    if getTwitter.is_authorized:
        value = getTwitter.get_trends_available(settings.YAHOO_CONSUMER_KEY)
    else:
        global profile_track
        profile_track = 'twitter'
        twitter_url = getTwitter.get_authorize_url()
        return HttpResponseRedirect(twitter_url)

    context ={'title': 'twitter', 'value': value}
    return render(request, 'hackathon/twitter.html', context)

def twitterTweets(request):
    print getTwitter.is_authorized
    if getTwitter.is_authorized:
        if request.method == 'GET':
            if request.GET.items():
                tweets = request.GET.get('tweets')
                content, jsonlist = getTwitter.get_tweets(tweets)
            else:
                content, jsonlist = '', ''
    else:
        global profile_track
        profile_track = 'twitter'
        twitter_url = getTwitter.get_authorize_url()
        return HttpResponseRedirect(twitter_url)

    context ={'title': 'twitter tweet', 'content': content, 'data': jsonlist}
    return render(request, 'hackathon/twitter_tweet.html', context)


##################
#  LINKEDIN  API #
##################

def linkedin(request):
    if getLinkedIn.is_authorized:
        content = getLinkedIn.getUserInfo()
    else:
        global profile_track
        profile_track = 'linkedin'
        linkedin_url = getLinkedIn.get_authorize_url()
        return HttpResponseRedirect(linkedin_url)

    context = {'title': 'linkedin example', 'content': content}
    return render(request, 'hackathon/linkedin.html', context)


#########################
# Snippet RESTful Model #
#########################

class CRUDBaseView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass

class SnippetView(CRUDBaseView):
    serializer_class = SnippetSerializer
    queryset = Snippet.objects.all()


##################
#   Twilio API   #
##################

def twilio(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        message = request.POST.get('message')
        sendSMS(str(message), str(number), '+13473781813')
        context = {'message': 'Your message has been sent successfully!'}
        return HttpResponseRedirect('/hackathon/api/')
    return render(request, 'hackathon/twilio.html')


######################
# Registration Views #
######################

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
            return HttpResponseRedirect('/hackathon/login/')
        else:
            print user_form.errors
    else:
        user_form = UserForm()


    return render(request,
            'hackathon/register.html',
            {'user_form': user_form, 'registered': registered} )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/hackathon/api/')
            else:
                return HttpResponse("Your Django Hackathon account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'hackathon/login.html', {})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/hackathon/login/')


def instagram_login(request):
    global profile_track
    profile_track = 'instagram'
    instagram_url = getInstagram.get_authorize_url()
    return HttpResponseRedirect(instagram_url)

def tumblr_login(request):
    global profile_track
    profile_track = 'tumblr'
    tumblr_url = getTumblr.authorize_url()
    return HttpResponseRedirect(tumblr_url)

def twitter_login(request):
    global profile_track
    profile_track = 'twitter'
    twitter_url = getTwitter.get_authorize_url()
    return HttpResponseRedirect(twitter_url)

def github_login(request):
    global profile_track
    profile_track = 'github'
    github_url = getGithub.get_authorize_url()
    return HttpResponseRedirect(github_url)

def linkedin_login(request):
    global profile_track
    profile_track = 'linkedin'
    linkedin_url = getLinkedIn.get_authorize_url()
    return HttpResponseRedirect(linkedin_url)

def facebook_login(request):
    global profile_track
    profile_track = 'facebook'
    facebook_url = getFacebook.get_authorize_url()
    return HttpResponseRedirect(facebook_url)


def google_login(request):
    global profile_track
    profile_track = 'google'
    google_url = getGoogle.get_authorize_url()
    return HttpResponseRedirect(google_url)

def dropbox_login(request):
    global profile_track
    profile_track = 'dropbox'
    dropbox_url = getDropbox.get_authorize_url()
    return HttpResponseRedirect(dropbox_url)

def foursquare_login(request):
    global profile_track
    profile_track = 'foursquare'
    forsquare_url = getFoursquare.get_authorize_url()
    return HttpResponseRedirect(forsquare_url)
