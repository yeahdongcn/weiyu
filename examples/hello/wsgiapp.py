#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app
# NOTE: the recommended way to run this example is to copy the example
# directory into a virtualenv. symlinks can prevent Python from locating
# weiyu's libraries!
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

from weiyu.registry.loader import JSONConfig
from weiyu.adapters.wsgi import WeiyuWSGIAdapter

from weiyu.__version__ import VERSION_STR
from weiyu.registry.provider import request, _registries as REGS
from weiyu.rendering import Hub
from weiyu.rendering.base import RenderContext

OUTPUT_ENC = 'utf-8'

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()

# trigger registration of Mako template handler
from weiyu.rendering.makorenderer import MakoRenderable


def get_response(env, conf):
    tmpl = Hub.get_template('mako', 'env.html')
    result = tmpl.render(RenderContext(
            env=env,
            regs=REGS,
            sitename=conf['name'],
            version=VERSION_STR,
            ))
    return result.encode(OUTPUT_ENC)


def env_test_worker(request):
    return (
            200,
            {'Content-Type': 'text/html; charset=utf-8', },
            iter([get_response(request.environ, request.site), ]),
            )


application = WeiyuWSGIAdapter(env_test_worker)


if __name__ == '__main__':
    import sys
    from socket import gethostname

    DEFAULT_PORT = 9090

    try:
        from cherrypy import wsgiserver
    except ImportError:
        print >>sys.stderr, 'no cherrypy, plz run via an external wsgi server'
        sys.exit(1)

    if len(sys.argv) > 2:
        print >>sys.stderr, 'usage: %s [port=%d]' % (sys.argv[0], DEFAULT_PORT)
        sys.exit(2)

    port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PORT

    server = wsgiserver.CherryPyWSGIServer(
            ('0.0.0.0', port),
            application,
            server_name=gethostname(),
            )

    server.start()


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8: