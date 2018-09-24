# -*- coding: utf-8 -*-
import unittest

from versature.storage import DictionaryStorage
from config import access_config


class SubscriptionsTest(unittest.TestCase):

    def setUp(self):
        self.dict_storage = DictionaryStorage()

    def test_create_sub_office_manager(self):
        result = access_config.versature.create_subscription(post_uri="https://1-8-128-dot-versature-integrate-2-test.appspot.com/api/subscriptions/test_post_uri/", expires_in=7200, calls=True)
        self.assertIsNotNone(result)
