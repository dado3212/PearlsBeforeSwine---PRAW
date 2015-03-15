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

running = True
while running:
	curr_date = "{dt.month}/{dt.day}/{year}".format(dt = datetime.datetime.now(pytz.timezone('US/Eastern')), year = strftime('%y'))
	start = 'Pearls ' + curr_date + ': '

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
	sleep(120) #wait for 2 minutes (minus 8 seconds)