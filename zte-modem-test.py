#!/usr/bin/python
# coding: utf8

from time import sleep, localtime, strftime
from base64 import b64encode

import sys
import logging
import requests

# file_handler = logging.FileHandler(filename='tmp.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('ZTE-API')

class Modem:
    """Manage ZTE modem via python script"""

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
        """get auth session for future requests"""
        headers = {
            "Referer": self.referer
        }

        if self.pwd is None:
            admin_data_url = f"{self.get_data_url}?cmd=admin_Password&multi_data=0"
            admin_data_request = requests.get(admin_data_url, headers=headers, timeout=10)
            admin_data = admin_data_request.json()

            self.pwd = admin_data["admin_Password"]

        encoded_password = b64encode(bytes(self.pwd, "utf-8")).decode()

        session = requests.Session()
        session.headers.update(headers)

        session.post(self.set_data_url, {
            **self.common_req_params,
            "goformId": "LOGIN",
            "password": encoded_password,
        })

        return session

    def get_info(self, fields = None):
        """get info"""

        if fields is None:
            logging.error("get_info empty fields")
            sys.exit(0)

        session = self.__get_auth_session()

        params = {
            **self.common_req_params,
            "multi_data": 1,
            "cmd": ",".join(fields),
        }

        request = session.get(self.get_data_url, params=params)

        logging.info(request.json())

        return request.json()

    def get_base_info(self):
        """ get_base_info """
        fields = [
            "lte_rssi",
            "lte_band",
            "lte_rsrq",
            "lte_pci",
            "lte_rsrp",
            "lte_snr",
            "tx_power",
            "cell_id",
            "rssi",
            "rscp",
            "network_type",
            "signalbar",
            "imei",

            "battery_vol_percent",
            "battery_pers",
            "battery_charging",
            "battery_vol_percent",
            "battery_status",

            "ppp_status",
            "wa_inner_version",
            "realtime_rx_bytes",
            "realtime_rx_thrpt",
            "realtime_time",
            "realtime_tx_bytes",
            "realtime_tx_thrpt",
            "peak_tx_bytes",
            "peak_rx_bytes",
            "data_status",
        ]


        # hass.states.set('sensor.zte_test', self.get_info(fields)['lte_rssi'])
        # logger.info('test', self.get_info(fields)['lte_rssi'])
        print(self.get_info(fields))
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

    def sms_get_status_info(self, sms_cmd = None):
        """ sms_cmd_status_info """

        if sms_cmd is None:
            sms_cmd = 4

        params = {
            **self.common_req_params,
            "cmd": ",".join(["sms_cmd_status_info"]),
            "sms_cmd": sms_cmd
        }

        session = self.__get_auth_session()
        request = session.get(self.get_data_url, params=params)

        logger.info(request.json())

        return request.json()

    def sms_get_info(self, unread_only: bool = False):
        """read sms from device"""

        tags = 1 if unread_only is True else 10

        params = {
            **self.common_req_params,
            "cmd": ",".join(["sms_data_total"]),
            "page": 0,
            "data_per_page": 500,
            "mem_store": 1,
            "tags": tags,
            "order_by": "order+by+id+desc"
        }

        session = self.__get_auth_session()
        request = session.get(self.get_data_url, params=params)
        messages = request.json()['messages']

        result = list(map(self.__sms_parse, messages))
        logger.info(result)

    def __sms_parse(self, sms):

        sms["content"] = bytes.fromhex(sms["content"]).decode('utf-16-be')

        return sms


    def sms_send(self, number: str, text: str):
        """send sms"""

        number = str(number)

        if number.startswith("+") is False:
            logging.error("Phone number must start with + ")
            sys.exit(0)

        msg = "".join(f"{c:02x}" for c in text.encode("utf-16-be"))
        time = strftime("%y;%m;%d;%H;%M;%S;+0", localtime())

        session = self.__get_auth_session()
        request = session.post(self.set_data_url, {
            **self.common_req_params,
            "notCallback": "true",
            "goformId": "SEND_SMS",
            "isTest": "false",
            "Number": number,
            "sms_time": time,
            "MessageBody": msg,
            "encode_type": "UNICODE",
            "ID": "-1"
        })


        logging.info(request.json())
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

IP = "192.168.32.1"
command = sys.argv[1] or "baseinfo"
zte_api = Modem(IP)

if command == "reconnect":
    zte_api.reconnect()

if command == "restart":
    zte_api.restart()

if command == "baseinfo":
    zte_api.get_base_info()

if command == "sms":
    zte_api.sms_get_info(unread_only = True)

if command == "sms_send":
    zte_api.sms_send(number="+79264094805", text="Привет с дачи")

if command == "test":
    zte_api.sms_get_status_info(sms_cmd = 15)
