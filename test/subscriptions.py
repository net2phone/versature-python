# -*- coding: utf-8 -*-
import unittest

from versature.storage import DictionaryStorage
from config import office_manager_config, client_credential_config


class SubscriptionsTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.client_credentials = client_credential_config()
        self.dict_storage = DictionaryStorage()


    def test_create_sub_office_manager(self):
        result = self.office_manager.versature.create_subscription(post_uri="https://1-8-128-dot-versature-integrate-2-test.appspot.com/api/subscriptions/test_post_uri/", expires_in=7200, calls=True)
        #    def create_subscription(self, post_uri, expires_in=7200, calls=False, cdrs=False, cdr_creation=False, recordings=False, recording_analytics=False, raw=False, user='*', **kwargs):
        self.assertIsNotNone(result)
