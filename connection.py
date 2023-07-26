#!/usr/bin/python

# coding: utf8

from time import gmtime, strftime
import urllib
import urllib.parse
import sys
import time

import base64
import requests
import logging

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

host=sys.argv[1]
url = 'http://{}/goform/goform_set_cmd_process'.format(host)
authUrl = "http://{}/goform/goform_get_cmd_process?cmd=admin_Password&multi_data=0".format(host)

# get admin password
def getSession():
	headers = {
		'Referer': 'http://{}/index.html'.format(host)
	}

	try:
		adminData = requests.request("GET", authUrl, headers=headers)

		adminData = adminData.json()
		password = adminData['admin_Password'];
		encodedPassword = base64.b64encode(bytes(password, 'utf-8')).decode()

		#logging.info(encodedPassword);
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

		return s;
	except Exception as exception:
		logging.error(type(exception).__name__)

		return None;

def main():
	command=sys.argv[2]
	session = getSession()

	if session == None :
		logging.error('Session not started')

		exit()

	if command == 'reload' :

		logging.info('DISCONNECT_NETWORK')
		session.post(url, {
			'goformId' : 'DISCONNECT_NETWORK',
			'isTest' : 'false'
		})

		time.sleep(5)

		logging.info('CONNECT_NETWORK')
		session.post(url, {
			'goformId' : 'CONNECT_NETWORK',
			'isTest' : 'false'
		})
		session.close()

	if command == 'restart' :
		logging.info('REBOOT_DEVICE')

		try:
			session.post(url, {
				'goformId' : 'REBOOT_DEVICE',
				'isTest' : 'false'
			})

		except requests.exceptions.ReadTimeout:
			pass

		session.close()
main()