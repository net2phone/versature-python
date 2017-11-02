# -*- coding: utf-8 -*-
import unittest

from config import office_manager_config, client_credential_config


__author__ = 'DavidWard'


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.client_credentials = client_credential_config()

    ##################
    #### Get CDRs ####
    ##################

    def test_get_users_for_domain_office_manager(self):
        result = self.office_manager.versature.users()
        self.assertIsNotNone(result)