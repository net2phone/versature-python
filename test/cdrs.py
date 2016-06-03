# -*- coding: utf-8 -*-
import unittest

from config import office_manager_config

__author__ = 'DavidWard'


class CDRsTest(unittest.TestCase):

    ##################
    #### Get CDRs ####
    ##################

    def test_get_cdrs_for_domain_office_manager(self):
        result = office_manager_config.versature.get_cdrs(all=True)
        self.assertIsNotNone(result)

    def test_get_cdrs_for_user_office_manager(self):
        result = office_manager_config.versature.get_cdrs()
        self.assertIsNotNone(result)