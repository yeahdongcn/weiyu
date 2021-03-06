#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / command line / subcommands / shell
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

from .. import discover


def rain_shell(args):
    discover.init_or_die(args)

    try:
        # prefer IPython as console!
        import IPython
        IPython.embed()
        return 0
    except ImportError:
        pass

    # fallback to using code module
    import code
    console = code.InteractiveConsole()
    console.interact()

    return 0


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
