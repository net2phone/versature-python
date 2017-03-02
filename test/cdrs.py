# -*- coding: utf-8 -*-
import unittest

from config import office_manager_config, client_credential_config


__author__ = 'DavidWard'


class CDRsTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.client_credentials = client_credential_config()

    ##################
    #### Get CDRs ####
    ##################

    def test_get_cdrs_for_domain_office_manager(self):
        result = self.office_manager().versature.cdrs(all=True)
        self.assertIsNotNone(result)

    def test_get_cdrs_for_user_office_manager(self):
        result = self.office_manager().versature.cdrs()
        self.assertIsNotNone(result)

    def test_client_credential_domain_cdrs(self):
        result = self.client_credentials.versature.cdrs(all=True)
        self.assertIsNotNone(result)