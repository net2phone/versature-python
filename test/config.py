# -*- coding: utf-8 -*-

from versature.storage import DictionaryStorage
from versature.resources import Versature
from secrets import VERSATURE_API_URL, VERSATURE_CLIENT_ID, VERSATURE_CLIENT_SECRET, VERSATURE_VENDOR_ID, OFFICE_MANAGER_USER, \
    OFFICE_MANAGER_DOMAIN, OFFICE_MANAGER_PASSWORD, BASIC_USER_USER, BASIC_USER_DOMAIN, BASIC_USER_PASSWORD, \
    RESELLER_USER, RESELLER_DOMAIN, RESELLER_PASSWORD, CALL_QUEUE_USER


__author__ = 'DavidWard'


class Config(object):

    def __init__(self, api_url, client_id, user=None, domain=None, password=None, client_secret=None, vendor_id=None, call_queue_user=None, storage=None):
        self.api_url = api_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.vendor_id = vendor_id
        self.user = user
        self.domain = domain
        self.password = password
        self.call_queue_user = call_queue_user
        #self.storage = storage
        self.storage = DictionaryStorage()

    @property
    def username(self):
        return '%s@%s' % (self.user, self.domain) if self.user and self.domain else None

    @property
    def versature(self):
        return Versature(username=self.username, password=self.password, client_id=self.client_id,
                         client_secret=self.client_secret, vendor_id=self.vendor_id, api_url=self.api_url, storage=self.storage)


def client_credential_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, client_secret=VERSATURE_CLIENT_SECRET)


def office_manager_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=OFFICE_MANAGER_USER, domain=OFFICE_MANAGER_DOMAIN, password=OFFICE_MANAGER_PASSWORD,
                  call_queue_user=CALL_QUEUE_USER)


def base_user_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=BASIC_USER_USER, domain=BASIC_USER_DOMAIN, password=BASIC_USER_PASSWORD)


def reseller_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=RESELLER_USER, domain=RESELLER_DOMAIN, password=RESELLER_PASSWORD)
