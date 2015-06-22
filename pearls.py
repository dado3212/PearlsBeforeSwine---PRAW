#! /usr/bin/python

## IMPORT STATEMENTS ##
import praw
import datetime
import pytz
import re
import requests
import cPickle as pickle
from time import sleep, strftime
from nltk.corpus import words

import logging
logging.captureWarnings(True) #because running 2.7.6
requests.packages.urllib3.disable_warnings()

## DEFINITION OF VARIABLES ##
USERNAME = 'Pearls_Bot'
PASSWORD = 'password'
USERAGENT = 'Pearls_Bot v1.2 by /u/dado3212'
globalFreq = pickle.load(open( "freq.dat", "rb"))

## LOGIN ##
r = praw.Reddit(USERAGENT)
r.login(USERNAME,PASSWORD)
sub = r.get_subreddit('PearlsBeforeSwine')

## GUESS TITLE ##
def guess_title(url):
	load = 'https://www.newocr.com/'

	invalidWords = 'pearls before swine'
	with requests.Session() as c:
		h = {'User-Agent':''}
		image = c.get(url,headers=h)

		comic = re.search("<img .*?class=\"strip\" src=\"(.*?)\"",image.text.encode('utf-8')).group(1)

		init = c.get(load, verify=False) # initializes the headers, cookies

		loadData = {"userfile":'',"url":comic,"preview":1}

		ocrLoad = c.post(load, data=loadData, verify=False)

		code = re.search("<input type=\"hidden\" name =\"u\" value=\"(.*?)\"",ocrLoad.text.encode('utf-8')).group(1)
		x1 = re.search("<input type=\"hidden\".*?name=\"x1\" value=\"(.*?)\"",ocrLoad.text.encode('utf-8')).group(1)
		x2 = re.search("<input type=\"hidden\".*?name=\"x2\" value=\"(.*?)\"",ocrLoad.text.encode('utf-8')).group(1)
		y1 = re.search("<input type=\"hidden\".*?name=\"y1\" value=\"(.*?)\"",ocrLoad.text.encode('utf-8')).group(1)
		y2 = re.search("<input type=\"hidden\".*?name=\"y2\" value=\"(.*?)\"",ocrLoad.text.encode('utf-8')).group(1)

		runData = {
			'l3':'eng',
			'l2[]':'eng',
			'r':0,
			'psm':3,
			'u':code,
			'x1':x1,
			'x2':x2,
			'y1':y1,
			'y2':y2,
			'ocr':1
		}
		
		ocrRun = c.post(load, data=runData, verify=False)

		wordImportance = {}
		guess = ""

		if '<strong>Error!</strong> Text can not be recognized.' in ocrRun.text:
			guess = 'No guess.'
		else:
			for word in re.search("<textarea id=\"ocr-result\".*?>([\s\S]*?)</textarea>",ocrRun.text.encode('utf-8')).group(1).split():
				word = re.compile('[^a-zA-Z\']').sub('',word).lower()
				freq = globalFreq[word]
				if word in words.words() and freq < 1000 and word not in invalidWords and len(word) > 2:
					wordImportance[word] = freq

			wordImportance = sorted(wordImportance, key=lambda x:wordImportance[x])

			for i in xrange(0,min(max(len(wordImportance)/3,3), len(wordImportance))):
				guess += wordImportance[i] + ' '

		return guess.capitalize()

## INTRO CODE ##

print ''
print '#####################################################################'
print '#                                                                   #'
print '#             		Pearls_Bot v1.2     		            #'
print '#                    created by /u/dado3212                         #'
print '#                                                                   #'
print '#                                                                   #'
print '#         Initializing program and beginning to scan... 	    #'
print '#                                                                   #'
print '#                                                                   #'
print '#####################################################################'


r.send_message('dado3212','Booting','Pearls_Bot initializing.')

## LOOP CODE ##

sent_message = ''

running = True
isFlaired = False
while running:
	dt = datetime.datetime.now(pytz.timezone('US/Eastern'))	# creates time object
	curr_date = "{dt.month}/{dt.day}/{year}".format(dt = dt, year = strftime('%y')) # gets the current date in the format mm/dd/yy, with no leading 0's
	start = 'Pearls ' + curr_date + ': ' # gets the start of today's strip post (to see if it's been posted)

	if (sent_message != curr_date):
		isFlaired = False

	curr_hour = datetime.datetime.now(pytz.timezone('US/Eastern')).hour # gets the current 24 hour 

	if (curr_hour == 15 and sent_message != curr_date): # if it's three pm 
		matches = 0
		todays = sub.search('title:"' + start + '"') # and it hasn't been posted
		for match in todays:
			matches+=1
		if (matches == 0): # send a message
			url = 'http://www.gocomics.com/pearlsbeforeswine/' + strftime('%Y/%m/%d')
			guess = guess_title(url)
			r.send_message('dado3212','Pearls Post - ' + curr_date,('The current comic has not yet been posted.  \n'
				'Title Guess: ' + guess + '  \n'
				'The link is [**here**](' + url + ').  \n'
				'The posting link is located [**here**](http://www.reddit.com/r/pearlsbeforeswine/submit?title=Pearls%20' + str(dt.month) + '/' + str(dt.day) + '/' + strftime('%y') + '%3A&url=http://www.gocomics.com/pearlsbeforeswine/' + strftime('%Y/%m/%d') + ').\n\n'
				'To cross post to /r/comics, the link is [**here**](http://www.reddit.com/r/comics/submit?title=%20-%20Pearls%20Before%20Swine&url=http://www.gocomics.com/pearlsbeforeswine/' + strftime('%Y/%m/%d') + ').'))
			sent_message = curr_date

	try:
		if not isFlaired:
			links = sub.get_new(limit=3) # get 3 newest posts

			for item in links:
				title = item.title # gets the submission title
				flair = item.link_flair_css_class # gets the flair information
				if title.startswith(start) and flair is None: # ie today's comic and unflaired
					# Remove flair from all others
					flaired = sub.search('NOT title:"' + title + '" AND flair:Current+Strip')
					for post in flaired:
						sub.set_flair(post,'','')

					# Flair it
					sub.set_flair(item,'Current Strip','current-strip')
					isFlaired = True
	except Exception as e:
		pass # nothing I'm gonna do, tbh
	sleep(120) # wait for 2 minutes
