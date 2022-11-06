# ZTE MF910 (Megafon MR150-2)

## connection.py

`python connection.py <router_ip> <reload|restart>`

- `python connection.py 192.168.1.1 reload` - disconnect and connect 3g/4g network
- `python connection.py 192.168.1.1 reload` - reboot device


## sendsms.py

`python sendsms.py <router_ip> <phone> <message>`

- `python sendsms.py 192.168.1.1 +79991112233 "sms from python cli"`

## Useful links

- [zte-modem-api-docs](https://wijayamin.github.io/zte-modem-api-docs/)
- [ZTE MF910 hacks](https://vulners.com/pentestpartners/PENTESTPARTNERS:098A34F42408499A17087DAE12C24A0C)