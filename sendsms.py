#!/usr/bin/python

# coding: utf8

from time import gmtime, strftime
import urllib
import urllib.parse
import sys

import base64
import requests

#import logging
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')


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


# Prepare sms
text=sys.argv[3]
text=text.encode("utf-16-be")
msg="".join("{:02x}".format(c) for c in text)

number=sys.argv[2]

time=strftime("%y;%m;%d;%H;%M;%S;+5", gmtime())

sms = urllib.parse.urlencode({
	'notCallback' : 'true',
	'goformId' : 'SEND_SMS',
	'isTest' : 'false',
	'Number' : number,
	'sms_time': time,
	'MessageBody': msg,
	'encode_type' : 'UNICODE',
	'ID' : '-1'}
)

#logging.info(sms)

s.post(url, sms)

