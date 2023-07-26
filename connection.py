"""Manage connection"""
#!/usr/bin/python
# coding: utf8

import sys
import time

import logging
import requests

import auth


def main():
    """ Manage modem connection """
    if len(sys.argv) <= 1:
        logging.error("host not defined")

        sys.exit(0)

    if len(sys.argv) <= 2:
        logging.error("command (reload or restart) not defined")

        sys.exit(0)


    host = sys.argv[1]
    command = sys.argv[2]

    url = f"http://{host}/goform/goform_set_cmd_process"
    session = auth.get_auth_session(host)

    if session is None:
        logging.error("Session not started")

        sys.exit(0)

    if command == "reload":

        logging.info("DISCONNECT_NETWORK")
        session.post(url, {
            "goformId": "DISCONNECT_NETWORK",
            "isTest": "false"
        })

        time.sleep(5)

        logging.info("CONNECT_NETWORK")
        session.post(url, {
            "goformId": "CONNECT_NETWORK",
            "isTest": "false"
        })
        session.close()

    if command == "restart":
        logging.info("REBOOT_DEVICE")

        try:
            session.post(url, {
                "goformId": "REBOOT_DEVICE",
                "isTest": "false"
            })

        except requests.exceptions.ReadTimeout:
            pass

        session.close()


main()
