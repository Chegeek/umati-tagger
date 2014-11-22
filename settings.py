#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Jun 18, 2014
@author: chalenge

General settings for the app! COnfigures the mail platform and the database from which it will retrieve data.
'''

#
flask_config = dict(
    DEBUG = True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL= False,
    MAIL_USERNAME = 'chalenge@ihub.co.ke',
    MAIL_PASSWORD = 'devapp',
    SECRET_KEY = 'MPF\xfbz\xfbz\xa7\xcf\x84\x8cd\rg\xd5\x04\xee\xa4\xd6\xb9]\xf8\x0e\xf3'
)

#dbase Configuration settings
dbase_config = {
  'user': 'postgres',
  # 'password': 'yadda',
  # 'host': 'localhost',
  'database': 'Umati',
  # 'port': 5432
}

