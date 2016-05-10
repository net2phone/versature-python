# -*- coding: utf-8 -*-

from integrate.request_handler import AuthenticatedResourceRequest

__author__ = 'David Ward'

RESOURCE_PATH = 'calls/'


def read_active_calls(all=False, **kwargs):
    authenticated_resource_request = AuthenticatedResourceRequest(**kwargs)
    params = {'all': all}
    return authenticated_resource_request.request('GET', params=params, path=RESOURCE_PATH)


def place_call(fr, to, auto_answer=False, **kwargs):
    authenticated_resource_request = AuthenticatedResourceRequest(**kwargs)
    params = {'to': to,
              'from': fr,
              'auto_answer': auto_answer}
    return authenticated_resource_request.request('POST', params=params, path=RESOURCE_PATH)


def answer_call(id, to, **kwargs):
    authenticated_resource_request = AuthenticatedResourceRequest(**kwargs)
    data = {'id': id, 'to': to}
    path = '%s/%s/answer/' % (RESOURCE_PATH, id)
    return authenticated_resource_request.request('PUT', data=data, path=path)


def terminate_call(id, **kwargs):
    authenticated_resource_request = AuthenticatedResourceRequest(**kwargs)
    path = '%s/%s' % (RESOURCE_PATH, id)
    return authenticated_resource_request.request('DELETE', path=path)