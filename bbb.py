#!/usr/bin/env python

import netifaces as ni

ip = ni.ifaddresses('ens160')[2][0]['addr']
print ip


