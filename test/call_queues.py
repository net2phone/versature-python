# -*- coding: utf-8 -*-
import sys
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

import unittest
import time
from datetime import datetime, timedelta

from config import office_manager_config

__author__ = 'DavidWard'


class CallQueuesTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.one_day_ago = datetime.utcnow() - timedelta(days=1)
        self.today = datetime.utcnow()


    #################################
    #### Login Call Queue Stats #####
    #################################

    def test_get_call_queues_stats(self):
        result = self.office_manager.versature.call_queue_stats(start_date=self.one_day_ago, end_date=self.today)
        self.assertIsNotNone(result)

    def test_get_call_queues_stats_async(self):
        request = self.office_manager.versature.call_queue_stats(async=True, start_date=self.one_day_ago, end_date=self.today)
        result = request.resolve()
        self.assertIsNotNone(result)

    def test_call_queue_agents_inbound(self):
        result = self.office_manager.versature.call_queue_agent_stats(start_date=self.one_day_ago, end_date=self.today,
                                                                      inbound=True, outbound=False, queue='8820')
        self.assertIsNotNone(result)

    def test_get_queue_agents_inbound(self):

        first_response = self.office_manager.versature.call_queue_agent_stats(start_date=self.one_day_ago, end_date=self.today,
                                                                       inbound=True, outbound=False, queue='8814',
                                                                       cache_timeout=30, use_storage=True)
        self.assertIsNotNone(first_response)

        time.sleep(30)

        second_response = self.office_manager.versature.call_queue_agent_stats(start_date=self.one_day_ago, end_date=self.today,
                                                                       inbound=True, outbound=False, queue='8814',
                                                                       cache_timeout=30, use_storage=True)
        self.assertIsNotNone(second_response)

    def test_expected_response(self):
        expected_support_first_names = ['Andre', 'Jonathon', 'Sam', 'Kole', 'Frank', 'Cameron']

        expected_sdr_first_names = ['Tyler', 'Jason', 'Alexa', 'Dean']

        def support_request():

            support_response = self.office_manager.versature.call_queue_agent_stats(start_date=self.one_day_ago,
                                                                                    end_date=self.today,
                                                                                    inbound=True, outbound=False,
                                                                                    queue='8814',
                                                                                    cache_timeout=60, use_storage=True)
            logging.info("Result: %s", support_response)
            self.assertIsNotNone(support_response)

            for agent in support_response:

                self.assertIn(agent.get('first_name'), expected_support_first_names, 'Found unexpected name in Support Response. Agent Data: %s' % agent)

                #if agent.get('first_name') not in expected_support_first_names:
                #    logging.error('Found unexpected name in Support Response. Agent Data: %s', agent)
                #    self.assertIn(agent.get('first_name'), expected_support_first_names)

        def sdr_request():

            sdr_response = self.office_manager.versature.call_queue_agent_stats(start_date=self.one_day_ago,
                                                                                    end_date=self.today,
                                                                                    inbound=True, outbound=False,
                                                                                    queue='8820',
                                                                                    cache_timeout=60, use_storage=True)
            logging.info("Result: %s", sdr_response)
            self.assertIsNotNone(sdr_response)

            for agent in sdr_response:
                self.assertIn(agent.get('first_name'), expected_sdr_first_names,
                              'Found unexpected name in SDR Response. Agent Data: %s' % agent)

                #if agent.get('first_name') not in expected_sdr_first_names:
                #    logging.error('Found unexpected name in SDR Response. Agent Data: %s', agent)
                #    self.assertIn(agent.get('first_name'), expected_sdr_first_names)

        for x in xrange(1, 10):
            logging.info("Begin Iteration")
            support_request()
            time.sleep(1)
            sdr_request()
            logging.info("Finish Iteration")
            time.sleep(20)
