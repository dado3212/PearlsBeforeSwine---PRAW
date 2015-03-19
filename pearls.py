#! /usr/bin/python

## IMPORT STATEMENTS ##
import praw
import datetime
import pytz
import re
from time import sleep, strftime

import logging
logging.captureWarnings(True) #because running 2.7.6

## DEFINITION OF VARIABLES ##
USERNAME = 'Pearls_Bot'
PASSWORD = 'password'
USERAGENT = 'Pearls_Bot v1.0 by /u/dado3212'

## LOGIN ##
r = praw.Reddit(USERAGENT)
r.login(USERNAME,PASSWORD)
sub = r.get_subreddit('PearlsBeforeSwine')

## INTRO CODE ##

print ''
print '#####################################################################'
print '#                                                                   #'
print '#             		Pearls_Bot v1.0     		            #'
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
while running:
	dt = datetime.datetime.now(pytz.timezone('US/Eastern'))	#creates time object
	curr_date = "{dt.month}/{dt.day}/{year}".format(dt = dt, year = strftime('%y')) #gets the current date in the format mm/dd/yy, with no leading 0's
	start = 'Pearls ' + curr_date + ': ' #gets the start of today's strip post (to see if it's been posted)

	curr_hour = datetime.datetime.now(pytz.timezone('US/Eastern')).hour #gets the current 24 hour 

	if (curr_hour == 17 and sent_message != curr_date): #if it's five pm
		matches = 0
		todays = sub.search('title:"' + start + '"') #and it hasn't been posted
		for match in todays:
			matches+=1
		if (matches == 0): #send a message
			r.send_message('dado3212','Pearls Post - ' + curr_date,'The current comic has not yet been posted.  \nThe link is [**here**](http://www.gocomics.com/pearlsbeforeswine/' + strftime('%Y/%m/%d') + ').  \nThe posting link is located [**here**](http://www.reddit.com/r/pearlsbeforeswine/submit?title=Pearls%20' + str(dt.month) + '/' + str(dt.day) + '/' + strftime('%y') + '%3A&url=http://www.gocomics.com/pearlsbeforeswine/' + strftime('%Y/%m/%d') + ').')
			sent_message = curr_date

	try:
		links = sub.get_new(limit=3) #get 3 newest posts

		for item in links:
			title = item.title #gets the submission title
			if title.startswith(start): #ie today's comic
				flair = item.link_flair_css_class

				# Remove flair from all others
				flaired = sub.search('NOT title:"' + title + '" AND flair:Current+Strip')
				for post in flaired:
					sub.set_flair(post,'','')
					print 'Removed flair from ' + post.title

				# Flair it
				if flair is None:
					sub.set_flair(item,'Current Strip','current-strip')
					print 'Added flair'
				else:
					print 'Already flaired'

		print '----'
	except Exception as e:
		print 'Error: ' + str(e)
	sleep(120) #wait for 2 minutes