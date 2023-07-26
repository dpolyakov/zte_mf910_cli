"""auth helper"""
#!/usr/bin/python
# coding: utf8

import urllib
import urllib.parse

import base64
import logging

import requests


def get_auth_session(host):
    """auth session for next requests."""
    headers = {
        "Referer": f"http://{host}/index.html"
    }
    base_url = f"http://{host}/goform/goform_set_cmd_process"
    auth_url = f"http://{host}/goform/goform_get_cmd_process?cmd=admin_Password&multi_data=0"

    try:
        # Get admin password
        admin_data = requests.request(
            "GET", auth_url, headers=headers, timeout=10)

        admin_data = admin_data.json()

        password = admin_data['admin_Password']
        encoded_password = base64.b64encode(bytes(password, 'utf-8')).decode()

        login_request_data = urllib.parse.urlencode({
            'goformId': 'LOGIN',
            'isTest': 'false',
            'password': encoded_password,
        })

        session = requests.Session()
        session.headers.update(headers)

        # Les`t auth and get cookies
        session.post(base_url, login_request_data)

        return session
    except Exception as exception:
        logging.error(type(exception).__name__)

        return None
