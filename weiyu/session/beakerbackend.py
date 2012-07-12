#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / session handling / Beaker integration
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

from beaker.session import Session, SessionObject
from . import session_hub


class BeakerSession(object):
    def __init__(self, options=None):
        self.options = options if options is not None else {}

    def preprocess(self, request):
        request.session = SessionObject(request.env, **self.options)

        return None

    def postprocess(self, response):
        request = response.request
        ctx = response.context
        session = request.session

        if session.accessed():
            session.persist()

            _headers = session.__dict__['_headers']
            if _headers['set_cookie']:
                cookie = _headers['cookie_out']
                if cookie:
                    # append the cookie to response
                    new_cookies = ctx.get('cookies', [])
                    new_cookies.append(cookie)
                    ctx['cookies'] = new_cookies

        return response


@session_hub.register_handler('beaker')
def beaker_session_handler(options=None):
    return BeakerSession(options)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
