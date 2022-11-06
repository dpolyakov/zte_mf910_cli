#!/usr/bin/python

# coding: utf8

from time import gmtime, strftime
import urllib
import urllib.parse
import sys
import time

import base64
import requests

host=sys.argv[1]

# get admin password

authUrl = "http://{}/goform/goform_get_cmd_process?cmd=admin_Password&multi_data=0".format(host)

headers = {
	'Referer': 'http://{}/index.html'.format(host)
}

adminData = requests.request("GET", authUrl, headers=headers)

adminData = adminData.json()
password = adminData['admin_Password'];
encodedPassword = base64.b64encode(bytes(password, 'utf-8')).decode()

#logging.info(encodedPassword);

url = 'http://{}/goform/goform_set_cmd_process'.format(host)

loginRequestData = urllib.parse.urlencode({
	'goformId' : 'LOGIN',
	'isTest' : 'false',
	'password' : encodedPassword,
})

s = requests.Session()
s.headers.update(headers)

# Les`t auth and get cookies
s.post(url, loginRequestData)

#logging.info(s.cookies);


command=sys.argv[2]

if command == 'reload' :

	print('DISCONNECT_NETWORK')
	s.post(url, {
		'goformId' : 'DISCONNECT_NETWORK',
		'isTest' : 'false'
	})

	time.sleep(5)

	print('CONNECT_NETWORK')
	s.post(url, {
		'goformId' : 'CONNECT_NETWORK',
		'isTest' : 'false'
	})
	s.close()

if command == 'restart' :
	s.post(url, {
		'goformId' : 'REBOOT_DEVICE',
		'isTest' : 'false'
	})
	s.close()
