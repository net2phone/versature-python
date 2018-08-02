# -*- coding: utf-8 -*-
import unittest

from versature.storage import DictionaryStorage
from config import office_manager_config, client_credential_config


__author__ = 'DavidWard'


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.client_credentials = client_credential_config()
        self.dict_storage = DictionaryStorage()

    ###################
    #### Get Users ####
    ###################

    def test_get_users_for_domain_office_manager(self):
        result = self.office_manager.versature.users()
        self.assertIsNotNone(result)

    def test_get_current_user(self):
        result = self.office_manager.versature.current_user()
        self.assertIsNotNone(result)

    def test_get_current_user_cache(self):

        result = self.office_manager.versature.current_user(cache_timeout=20, use_storage=True)
        self.assertIsNotNone(result)

        result = self.office_manager.versature.current_user(use_storage=True)
        self.assertIsNotNone(result)
