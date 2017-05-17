# -*- coding: utf-8 -*-
import urllib2
import codecs
import requests
url = r'http://www.ygys.net/ResumeTest.aspx'
payload = {'__VIEWSTATE':'aa'}
files = {'FileUpload1': (u'C:/Users/nantian/Downloads/王浩简历.doc', open(u'C:/Users/nantian/Downloads/王浩简历.doc', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}
r = requests.post(url, files=files)
# r.text
# html = urllib2.urlopen(url).read()
print r.text