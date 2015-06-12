#!/usr/bin/env python
#
# Copyright (C) 2015 Michael Brown 
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
import subprocess

from ycmd import responses
from ycmd import utils
from ycmd.completers.completer import Completer

from django_completeme.parser import TemplateInspector

try:
    from django_completeme.parser import TemplateInspector
except ImportError:
    raise ImportError(
        'Error importing django_completeme. Make sure the django_completeme '
        'submodule has been checked out In the YouCompleteMe folder, '
        'run "git submodule update --init --recursive"')


# TODO really can be anything. normally set ft=htmldjango handles this
HTMLDJANGO_FILETYPES = set(['html', 'htmldjango'])


class HtmlDjangoCompleter(Completer):

    def SupportedFiletypes(self):
        return HTMLDJANGO_FILETYPES

    def _GetDjangoInspector(self, request_data):
        filename = request_data['filepath']
        contents = request_data['file_data'][filename]['contents']
        line = request_data['line_num']
        # Jedi expects columns to start at 0, not 1
        column = request_data['column_num'] - 1
        return TemplateInspector(filename, line, column, contents)

    def _GetExtraData(self, completion):
        location = {}
        if completion.module_path:
            location['filepath'] = ToUtf8IfNeeded(completion.module_path)
        if completion.line:
            location['line_num'] = completion.line
        if completion.column:
            location['column_num'] = completion.column + 1

        if location:
            extra_data = {}
            extra_data['location'] = location
            return extra_data
        else:
            return None

    def ComputeCandidatesInner(self, request_data):
        script = self._GetDjangoInspector(request_data)
        return script.completions()
