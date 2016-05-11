# -*- coding: utf-8 -*-
import unittest

from versature.resources import Versature
from secrets import client_id, username, password, vendor_id

__author__ = 'DavidWard'


class CallQueuesTest(unittest.TestCase):

    def setUp(self):
        self.versature = Versature(username=username, password=password, client_id=client_id, vendor_id=vendor_id)

    ################################
    #### Login Call Queue Stats ####
    #################################

    def test_get_call_queues_stats(self):
        result = self.versature.get_call_queue_stats()
        self.assertIsNotNone(result)
