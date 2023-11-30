#!/usr/bin/python
# coding: utf8

import sys

import base64
import logging

from functools import reduce
from time import sleep

import requests

class Modem:
    """Manage ZTE modem via python script"""

    global sys
    global requests
    global base64
    global sleep

    def __init__(self, ip: str, pwd = None) -> None:
        self.ip = ip
        self.pwd = pwd
        self.referer = f"http://{ip}/index.html"
        self.get_data_url = f"http://{ip}/goform/goform_get_cmd_process"
        self.set_data_url = f"http://{ip}/goform/goform_set_cmd_process"
        self.common_req_params = {
            "isTest": "false",
        }
    def __get_auth_session(self):
        """get auth session for next requests."""
        headers = {
            "Referer": self.referer
        }

        if self.pwd is None:
            admin_data_url = f"{self.get_data_url}?cmd=admin_Password&multi_data=0"
            admin_data_request = requests.get(admin_data_url, headers=headers, timeout=10)
            admin_data = admin_data_request.json()

            self.pwd = admin_data["admin_Password"]

        encoded_password = base64.b64encode(bytes(self.pwd, "utf-8")).decode()

        session = requests.Session()
        session.headers.update(headers)

        session.post(self.set_data_url, {
            **self.common_req_params,
            "goformId": "LOGIN",
            "password": encoded_password,
        })

        return session

    def get_info(self, fields = []):
        """get info"""

        if len(fields) == 0:
            logging.error("get_info empty fields")
            sys.exit(0)

        session = self.__get_auth_session()

        params = {
            **self.common_req_params,
            "multi_data": 1,
            "cmd": ",".join(fields),
        }

        request = session.get(self.get_data_url, params=params)

        print(request.json())

        return request.json()

    def get_base_info(self):
        """ get_base_info """
        fields = [
            "lte_rssi",
            "lte_band",
            "lte_rsrq",
            "lte_pci",
            "lte_rsrp"
            "tx_power",
            "cell_id",
            "rssi",
            "rscp",
            "network_type",
            "signalbar",
            "battery_vol_percent",
            "ppp_status",
            "wa_inner_version",
            "realtime_rx_bytes",
            "realtime_rx_thrpt",
            "realtime_time",
            "realtime_tx_bytes",
            "realtime_tx_thrpt",
        ]

        return self.get_info(fields)

    def restart(self):
        """ reboot device"""

        session = self.__get_auth_session()
        logging.info("REBOOT_DEVICE")

        try:
            session.post(self.set_data_url, {
                **self.common_req_params,
                "goformId": "REBOOT_DEVICE",
            })

        except requests.exceptions.ReadTimeout:
            pass

        session.close()

    def reconnect(self):
        """restart wan/Cellular connection"""
        session = self.__get_auth_session()

        logging.info("DISCONNECT_NETWORK")

        session.post(self.set_data_url, {
            **self.common_req_params,
            "goformId": "DISCONNECT_NETWORK",
        })

        sleep(5)

        logging.info("CONNECT_NETWORK")
        session.post(self.set_data_url, {
            **self.common_req_params,
            "goformId": "CONNECT_NETWORK",
        })

        session.close()

    def sms_stat(self):
        session = self.__get_auth_session()

        params = {
            **self.common_req_params,
            "cmd": ",".join(["sms_data_total"]),
            "page": 0,
            "data_per_page": 10,
            "mem_store": 1,
            "tags": 10,
            "order_by": "order+by+id+desc"
        }

        request = session.get(self.get_data_url, params=params)
        print(request.json())
    # def __sms_parse(self, sms, wft):

    #     sms_content = bytes.fromhex(sms["content"]).decode('utf-16-be')
    #     print(wft)
    #     return wft

    # def sms_get(self):
    #     """get sms data"""
    #     session = self.__get_auth_session()

    #     cmd = [
    #         "sms_data_total",
    #     ]

    #     params = {
    #         **self.common_req_params,
    #         "cmd": ",".join(cmd),
    #         "page": 0,
    #         "data_per_page": 10,
    #         "mem_store": 1,
    #         "tags": 10,
    #         "order_by": "order+by+id+desc"
    #     }

    #     request = session.get(self.get_data_url, params=params)
    #     messages = request.json()["messages"]

    #     result = reduce(self.__sms_parse, messages)

    #     # print(request)


# ip = data.get("ip")
# command = data.get("command")

ip = "192.168.32.1"
command = "baseinfo"
zte_api = Modem(ip)

if command == "reconnect":
    zte_api.reconnect()

if command == "restart":
    zte_api.restart()

if command == "baseinfo":
    zte_api.get_base_info()

if command == "sms":
    zte_api.sms_stat()
