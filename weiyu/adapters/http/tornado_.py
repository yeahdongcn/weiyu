#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / http / Tornado adapter
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division

__all__ = [
            'WeiyuTornadoAdapter',
            ]


from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer

from ...helpers.misc import smartstr

from ...registry.provider import request as reg_request

from ...reflex.classes import ReflexRequest

from .base import BaseHTTPReflex
from .util import status_to_str, dummy_file_wrapper, send_content_iter
from .util import parse_form, gen_http_headers

_env_from_req = WSGIContainer.environ


class TornadoRequest(ReflexRequest):
    def __init__(self, tornado_req, site_conf):
        super(TornadoRequest, self).__init__(_env_from_req(tornado_req))
        self._native_request = tornado_req

        self.site = site_conf


class TornadoReflex(BaseHTTPReflex):
    def __init__(self):
        super(TornadoReflex, self).__init__()

    def _do_accept_request(self, tornado_req):
        return TornadoRequest(tornado_req, self.SITE_CONF)

    def _do_translate_request(self, request):
        t_req = request._native_request
        # decode the path bytestring
        # TODO: improve encoding handling here
        path = request.path = smartstr(t_req.path, 'utf-8', 'replace')

        # Move routing (much) earlier so we don't waste time in processing
        # requests impossible to fulfill.
        # Note that we don't pass in "request" at this moment. The object
        # can be replaced by potential hooks, and we certainly don't want
        # a reference to be frozen in the request.
        # Return value is of format (fn, args, kwargs, route_data, )
        route_result = self._do_routing(path)
        request.callback_info = route_result[:-1]
        request.route_data = route_result[-1]

        # Rest of request object preparation goes here...
        request.remote_addr = smartstr(t_req.remote_ip)
        method = request.method = smartstr(t_req.method)
        length, content = None, None
        try:
            content = t_req.body
        except AttributeError:
            pass

        request.content = content
        request.content_length = len(content) if content is not None else None

        if content is not None:
            # parse the POSTed data
            ctype = request.content_type = t_req.headers.get(
                    'CONTENT_TYPE',
                    None,
                    )
            if ctype == 'application/x-www-form-urlencoded':
                # decode the response for the view
                request.form = parse_form(content)

        # TODO: add more ubiquitous HTTP request headers

        # Session injection
        self.session.preprocess(request)

        return request

    def _start_response(self, response):
        content = response.content
        status_code = response.status
        enc = response.encoding

        t_req = response.request._native_request

        status_line, headers = gen_http_headers(response)

        # TODO: keep-alive things
        close_found = False
        for k, v in headers:
            if b'connection' == k.lower():
                close_found = True
                break
        if not close_found:
            headers.append((b'Connection', b'close', ))

        header_str = b'\r\n'.join(b'%s: %s' % hdr for hdr in headers)

        # Initiate the actual conversation
        t_req.write(b'HTTP/%s %s\r\n%s\r\n\r\n' % (
                b'1.1' if t_req.supports_http_1_1() else b'1.0',
                status_line, header_str,
                ))

        if response.is_raw_file:
            # push raw file
            return dummy_file_wrapper(response.raw_fp, response.raw_blksz)
        else:
            return send_content_iter(content, enc)

    def _do_deliver_response(self, response):
        req = response.request._native_request
        writer = req.write
        iterable = self._start_response(response)
        for chunk in iterable:
            writer(chunk)
        req.finish()


class WeiyuTornadoAdapter(HTTPServer):
    def __init__(self):
        self.__reflex = TornadoReflex()

        # the stimulate method is the callback
        # TODO: keep-alive, chunked encoding, and so on
        super(WeiyuTornadoAdapter, self).__init__(
                self.__reflex.stimulate,
                no_keep_alive=True,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
