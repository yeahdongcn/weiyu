#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / command line / subcommands / serve
#
# Copyright (C) 2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

from ...adapters import adapter_hub
from ...utils import server

from .. import discover


def rain_serve(args):
    discover.init_or_die(args)

    application = adapter_hub.make_app(args.adapter_type)
    server.cli_server(
            args.server_flavor,
            managed=True,
            application=application,
            port=args.port,
            )

    return 0


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
