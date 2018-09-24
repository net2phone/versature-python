# -*- coding: utf-8 -*-
import unittest

from versature.storage import DictionaryStorage
from config import access_config


__author__ = 'DavidWard'


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.dict_storage = DictionaryStorage()

    #####################
    #### Get Devices ####
    #####################

    def test_get_devices_for_domain_office_manager(self):
        result = access_config.office_manager.versature.devices()
        self.assertIsNotNone(result)

    def test_get_current_user_devices(self):
        result = access_config.office_manager.versature.current_user_devices()
        self.assertIsNotNone(result)
