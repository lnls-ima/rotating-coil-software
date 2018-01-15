# -*- coding: utf-8 -*-

# BSMP Exceptions

SRC_CLIENT = 'Client'
SRC_SERVER = 'Server'

class BSMPError(Exception):
    """Base class for exceptions in this module."""
    pass

class ServerError(BSMPError):
    """Raised if the server returned an unexpected error.

       Attributes:
            request -- packet that caused the error
            code -- code of the returned error"""
    def __init__(self, request, code):
        self.request = request
        self.code = code

class NoAnswerError(BSMPError):
    """Raised if the server did not answer a request.

       Attributes:
            request -- the packet that had no answer"""
    def __init__(self, request):
        self.request = request

class MalformedAnswerError(BSMPError):
    """Raised if the server answered with a malformed packet

       Attributes:
            request -- the packet that caused the rogue answer
            response -- the packet send by the server"""
    def __init__(self, request, response):
        self.request = request
        self.response = response

class SizeError(BSMPError):
    """Raised if the received message has an unexpected size

       Attributes:
            request -- the packet that caused the wrong answer
            response -- the wrong packet received"""
    def __init__(self, request, response, expected):
        self.request = request
        self.response = response


class CommandError(BSMPError):
    """Raised when a message contains an unexpected command code

       Attributes:
            request -- the packet that caused the wrong answer
            response -- the wrong packet received
            expected -- the expected command"""
    def __init__(self, request, response, expected):
        self.request = request
        self.response = response
        self.expected = expected

class ReadOnlyError(BSMPError):
    """Raised when an write operation is attempted on a read-only entity

       Attributes:
            entity -- the read-only entity"""
    def __init__(self,entity):
        self.entity = entity

class ArgumentError(BSMPError):
    """Raised when an invalid argument is passed to a method

       Attributes:
            name -- the name of the offending argument"""
    def __init__(self, name):
        self.name = name

class FunctionError(BSMPError):
    """Raised when a Function execution returns an error

       Attributes:
            code -- the error code"""
    def __init__(self, code):
        self.code = code
