import requests, grequests
import os
import gspread
import json
from jinja2 import Template

base_url = os.environ.get('BASE_URL', 'http://funnel.hasgeek.com/')
conf = os.environ.get('CONF_NAME', 'droidcon2012')
suffix = os.environ.get('SUFFIX', '/secret')
guser = os.environ.get('GUSER', None)
gpwd = os.environ.get('GPWD', None)

def fetch_funnel(url):
	r = requests.get(url)
	return r.json if r.status_code is 200 else {}	

def fetch_schedule():
	gc = gspread.login(guser, gpwd)
	wks0 = gc.open('Droidcon 2012 Schedule').worksheets()[0]
	wks1 = gc.open('Droidcon 2012 Schedule').worksheets()[1]
	return wks0, wks1

def insert_details(schedule):
	result = []
	for row in schedule:
		result.append([proposals.get(int(x)) if (x.isdigit() and int(x) > 0) else 'TBD' if (x.isdigit() and int(x) == 0) else x for x in row  ])
	return result

url = ''.join([base_url, conf, suffix])
data = fetch_funnel(url).get('proposals', None)
proposals = dict([(foo.get('id'), foo) for foo in data])
wks0, wks1 = fetch_schedule()
schedule1 =  insert_details(wks0.get_all_values())
schedule2 = insert_details(wks1.get_all_values())

print schedule1
print schedule2

#schedule = [schedule1,schedule2]
#print json.dumps(schedule)
