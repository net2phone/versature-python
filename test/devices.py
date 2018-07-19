# -*- coding: utf-8 -*-
import unittest
import time

from versature.storage import DictionaryStorage
from config import office_manager_config, client_credential_config


__author__ = 'DavidWard'


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.client_credentials = client_credential_config()
        self.dict_storage = DictionaryStorage()

    #####################
    #### Get Devices ####
    #####################

    def test_get_devices_for_domain_office_manager(self):
        result = self.office_manager.versature.devices()
        self.assertIsNotNone(result)

    def test_get_current_user_devices(self):
        result = self.office_manager.versature.current_user_devices()
        self.assertIsNotNone(result)
