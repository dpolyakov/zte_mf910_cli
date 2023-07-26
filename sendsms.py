""" Sending sms via modem """
#!/usr/bin/python
# coding: utf8

from time import gmtime, strftime

import sys
import urllib.parse
import logging

import auth


def send_sms():
    """ Send sms """
    if len(sys.argv) <= 1 :
        logging.error("host not defined")

        sys.exit(0)

    if len(sys.argv) <= 2:
        logging.error("recipient number not defined")

        sys.exit(0)

    if len(sys.argv) <= 3:
        logging.error("message is empty")

        sys.exit(0)

    host = sys.argv[1]
    number = sys.argv[2]
    text = sys.argv[3]

    # Prepare sms
    url = f"http://{host}/goform/goform_set_cmd_process"
    session = auth.get_auth_session(host)

    if session is None:
        logging.error("Session not started")

        sys.exit(0)

    text = text.encode("utf-16-be")

    msg = "".join(f"{c:02x}" for c in text)

    time = strftime("%y;%m;%d;%H;%M;%S;+5", gmtime())

    sms = urllib.parse.urlencode({
        "notCallback": "true",
        "goformId": "SEND_SMS",
        "isTest": "false",
        "Number": number,
        "sms_time": time,
        "MessageBody": msg,
        "encode_type": "UNICODE",
        "ID": "-1"
    })

    session.post(url, sms)


send_sms()
