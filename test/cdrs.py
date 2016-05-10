# -*- coding: utf-8 -*-
import unittest
from integrate.resources import authenitcate, cdrs


from secrets import client_id, username, password, vendor_id

__author__ = 'DavidWard'


class BaseAuthenticationTest(unittest.TestCase):

    def setUp(self):
        auth_details = authenitcate.login(username, password, client_id, vendor_id)
        self.access_token = auth_details['access_token']

    ########################################
    #### Login With Username & Password ####
    ########################################

    def test_get_cdrs(self):
        result = cdrs.get_cdrs(access_token=self.access_token)
        self.assertIsNotNone(result)
