# -*- coding: utf-8 -*-

from versature.storage import DictionaryStorage
from versature.resources import Versature
from secrets import VERSATURE_API_URL, VERSATURE_CLIENT_ID, VERSATURE_CLIENT_SECRET, VERSATURE_VENDOR_ID, OFFICE_MANAGER_USER, \
    OFFICE_MANAGER_DOMAIN, OFFICE_MANAGER_PASSWORD, BASIC_USER_USER, BASIC_USER_DOMAIN, BASIC_USER_PASSWORD, \
    RESELLER_USER, RESELLER_DOMAIN, RESELLER_PASSWORD, CALL_QUEUE_USER, CALL_CENTER_SUPERVISOR_DOMAIN, \
    CALL_CENTER_SUPERVISOR_USER, CALL_CENTER_SUPERVISOR_PASSWORD


__author__ = 'DavidWard'


class Config(object):

    def __init__(self, api_url, client_id, user=None, domain=None, password=None, client_secret=None, vendor_id=None,
                 call_queue_user=None, storage=None):
        self.api_url = api_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.vendor_id = vendor_id
        self.user = user
        self.domain = domain
        self.password = password
        self.call_queue_user = call_queue_user
        self.storage = storage

    @property
    def username(self):
        return '%s@%s' % (self.user, self.domain) if self.user and self.domain else None

    @property
    def versature(self):
        return Versature(username=self.username, password=self.password, client_id=self.client_id,
                         client_secret=self.client_secret, vendor_id=self.vendor_id, api_url=self.api_url,
                         storage=self.storage)


def client_credential_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, client_secret=VERSATURE_CLIENT_SECRET,
                  storage=DictionaryStorage())


def office_manager_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=OFFICE_MANAGER_USER, domain=OFFICE_MANAGER_DOMAIN, password=OFFICE_MANAGER_PASSWORD,
                  call_queue_user=CALL_QUEUE_USER, storage=DictionaryStorage())


def base_user_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=BASIC_USER_USER, domain=BASIC_USER_DOMAIN, password=BASIC_USER_PASSWORD,
                  storage=DictionaryStorage())


def reseller_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=RESELLER_USER, domain=RESELLER_DOMAIN, password=RESELLER_PASSWORD, storage=DictionaryStorage())


def call_center_supervisor_config():
    return Config(api_url=VERSATURE_API_URL, client_id=VERSATURE_CLIENT_ID, vendor_id=VERSATURE_VENDOR_ID,
                  user=CALL_CENTER_SUPERVISOR_USER, domain=CALL_CENTER_SUPERVISOR_DOMAIN,
                  password=CALL_CENTER_SUPERVISOR_PASSWORD,
                  call_queue_user=CALL_QUEUE_USER, storage=DictionaryStorage())


class AccessConfig(object):

    def __getattr__(self, name):

        if name == 'client_credential':
            client_credential = client_credential_config()
            setattr(self, 'client_credential', client_credential)
            return client_credential

        elif name == 'office_manager':
            office_manager = office_manager_config()
            setattr(self, 'office_manager', office_manager)
            return office_manager

        elif name == 'basic_user':
            basic_user = base_user_config()
            setattr(self, 'basic_user', basic_user)
            return basic_user

        elif name == 'reseller':
            reseller = reseller_config()
            setattr(self, 'reseller', reseller)
            return reseller

        elif name == 'call_center_supervisor':
            call_center_supervisor = call_center_supervisor_config()
            setattr(self, 'call_center_supervisor', call_center_supervisor)
            return call_center_supervisor

        else:
            raise AttributeError(name)


access_config = AccessConfig()

