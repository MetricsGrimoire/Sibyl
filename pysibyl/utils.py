#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012-2014 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Santiago Dueñas <sduenas@bitergia.com>
#   Daniel Izquierdo Cortazar <dizquierdo@bitergia.com>
#   

import json

class Parser(object):
    """Abstract parsing class.

    :param stream: stream to parse
    :type stream: str
    """

    def __init__(self, stream):
        self.stream = stream
        self._data = None

    def parse(self):
        """Parse the given stream

        Abstract method. Returns the parsed data.
        """
        raise NotImplementedError

    @property
    def data(self):
        """Returns the parsed data.

        :rtype: object
        """
        return self._data




class JSONStruct(dict):
    """Structure to store JSON objects from a stream."""

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


class JSONException(Exception):
    """Base class exception.

    Derived classes can overwrite error message declaring
    'message property.
    """

    message = 'Unknown error'

    def __init__(self, **kwargs):
        super(JSONException, self).__init__(kwargs)
        self.msg = self.message % kwargs

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return unicode(self.msg)


class ParserError(JSONException):
    """Base exception class for parser errors.

    Parser exceptions should derive from this class.
    """
    message = 'error parsing stream'


class JSONParserError(ParserError):
    """Exception raised when an error occurs parsing a JSON stream.

    :param error: explanation of the error
    :type error: str
    """
    message = 'error parsing JSON. %(error)s'


class JSONParser(Parser):
    """Generic JSON parser.

    :param stream: stream to parse
    :type stream: str
    """
    def __init__(self, stream):
        super(JSONParser, self).__init__(stream)

    def parse(self):
        """Parse the JSON stream.

        :returns: returns the parser data
        :rtype: JSONStruct
        :raises TypeError: when the json to parse is not a instance of str.
        :raises JSONParserError: when an error occurs parsing the stream.
        """
        if not isinstance(self.stream, str) and not isinstance(self.stream, unicode):
            raise TypeError('expected type str or unicode in stream parameter.')

        try:
            self._data = json.loads(self.stream, object_hook=JSONStruct)
        except Exception, e:
            raise JSONParserError(error=repr(e))

