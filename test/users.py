# -*- coding: utf-8 -*-
import unittest

from versature.storage import DictionaryStorage
from config import access_config


__author__ = 'DavidWard'


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.dict_storage = DictionaryStorage()

    ###################
    #### Get Users ####
    ###################

    def test_get_users_for_domain_office_manager(self):
        result = access_config.office_manager.versature.users()
        self.assertIsNotNone(result)

    def test_get_current_user(self):
        result = access_config.office_manager.versature.current_user()
        self.assertIsNotNone(result)

    def test_get_current_user_cache(self):

        result = access_config.office_manager.versature.current_user(cache_timeout=20)
        self.assertIsNotNone(result)

        result = access_config.office_manager.versature.current_user()
        self.assertIsNotNone(result)

    def test_voicemail_count(self):
        result = access_config.office_manager.versature.voicemails_count(user=self.office_manager.user)
        self.assertIsNotNone(result)