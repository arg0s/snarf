import requests, grequests
import os
import gspread

base_url = os.environ.get('BASE_URL', 'http://funnel.hasgeek.com/')
conf = os.environ.get('CONF_NAME', 'droidcon2012')
suffix = os.environ.get('SUFFIX', '/secret')
guser = os.environ.get('GUSER', None)
gpwd = os.environ.get('GPWD', None)

def fetch_funnel(url):
	r = requests.get(url)
#	import pdb; pdb.set_trace()
	return r.json if r.status_code is 200 else {}	

def fetch_worksheet():
	gc = gspread.login(guser, gpwd)
	wks = gc.open('Droidcon 2012 - Program Committee Planner').worksheets()[0]
	return wks

def fetch_schedule():
	gc = gspread.login(guser, gpwd)
	wks = gc.open('Droidcon 2012 - Program Committee Planner').worksheets()[1]
	print wks.get_all_values()
	return wks

def fetch_ratings():
	wks = fetch_worksheet()
	print wks


def update_proposal(sheet, proposal):
	#
	# JSON format of the HasGeek Funnel
	# {u'confirmed': False, u'name': u'556-writing-toolkits-frameworks-and-plugins-a-developer-masterclass-in-writing-re-usable-code', u'title': u'Writing Toolkits, Frameworks and Plugins. A Developer Masterclass in Writing Re-usable Code.', u'url': u'http://funnel.hasgeek.com/droidcon2012/556-writing-toolkits-frameworks-and-plugins-a-developer-masterclass-in-writing-re-usable-code', u'section': u'General Topics', u'level': u'Advanced', u'votes': 1, u'submitted': u'2012-10-08T23:33:17', u'email': None, u'proposer': u'James Hugman', u'phone': None, u'speaker': u'James Hugman', u'comments': 0, u'type': u'Lecture', u'id': 556}
	# Grab the entry, add it if it doesnt exist, modify existing entry if it does
	#
	try:
		# Lookup entry
		#import pdb; pdb.set_trace()
		cell = sheet.find(str(proposal.get(u'id')))
		# Update cells - real kludgy wudgy since gsheet doesnt seem to have a row update api
		row, col = cell.row, cell.col
		data = [proposal.get('id'), proposal.get('votes'), proposal.get('confirmed'), proposal.get('title'), proposal.get('speaker'), proposal.get('url'), proposal.get('level'), proposal.get('type'), proposal.get('section'), proposal.get('email'), proposal.get('phone')]
		for idx, value in enumerate(data):
			sheet.update_cell(row, col+idx, value)
		print ">> Updating row %i - proposal by %s" % (row, proposal.get('speaker'))
	except gspread.exceptions.CellNotFound:
		# Doesnt exist, push a new one if the speaker section exists (proposals are filtered)
		if proposal.get('speaker') is not None:
			data = [proposal.get('id'), proposal.get('votes'), proposal.get('confirmed'), proposal.get('title'), proposal.get('speaker'), proposal.get('url'), proposal.get('level'), proposal.get('type'), proposal.get('section'), proposal.get('email'), proposal.get('phone')]
			sheet.append_row(data)
			print ">> Adding proposal by %s" % proposal.get('speaker')


def bootstrap():
	# Load up the worksheet
	# Get the funnel feed
	# Update the sheets data while leaving the protected cells intact
	url = ''.join([base_url, conf, suffix])
	feed = fetch_funnel(url)
	proposals = feed.get('proposals', None)
	sheet = fetch_worksheet()
	#import pdb; pdb.set_trace()
	if proposals:
		[update_proposal(sheet, proposal) for proposal in proposals]
	else:
		print '>> Unable to fetch proposals'

bootstrap()
#print fetch_schedule()