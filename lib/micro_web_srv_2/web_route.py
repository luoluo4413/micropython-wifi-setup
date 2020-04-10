# The MIT License (MIT)
# Copyright 2019 Jean-Christophe Bos & HC2 (www.hc2.fr)

import re
import sys

import logging


_logger = logging.getLogger("route")


# ============================================================================
# ===( @WebRoute decorator )==================================================
# ============================================================================


def WebRoute(method=None, routePath=None):

    if not method or not routePath:
        raise ValueError("[@WebRoute] arguments are required for this decorator.")

    def decorated(handler):
        RegisterRoute(handler, method, routePath)
        _logger.info("[@WebRoute] %s %s" % (method, routePath))
        return handler

    return decorated


# ============================================================================
# ===( RegisterResult )=======================================================
# ============================================================================


def RegisterRoute(handler, method, routePath):
    if not isinstance(handler, type(lambda: None)):
        raise ValueError('"handler" must be a function.')
    if not isinstance(method, str) or len(method) == 0:
        raise ValueError('"method" requires a not empty string.')
    if not isinstance(routePath, str) or len(routePath) == 0:
        raise ValueError('"routePath" requires a not empty string.')
    if routePath[0] != "/":
        raise ValueError('"routePath" must start with a "/".')
    method = method.upper()
    if len(routePath) > 1 and routePath.endswith("/"):
        routePath = routePath[:-1]
    # Route -> '/users/<uID>/addresses/<addrID>/test/<anotherID>'
    # Regex -> '/users/(\w*)/addresses/(\w*)/test/(\w*)$'
    # Args  -> ['uID', 'addrID', 'anotherID']
    argNames = []
    regex = ""
    try:
        for i, part in enumerate(routePath.lower().split("/")):
            if i > 0:
                if part.startswith("<") and part.endswith(">"):
                    argName = part[1:-1]
                    if not argName:
                        raise Exception
                    argNames.append(argName)
                    regex += "/([\\w.]*)"
                else:
                    regex += "/" + part
        regex = re.compile(regex + "$")
    except:
        raise ValueError('Bad route path: "%s".' % routePath)
    for regRoute in _registeredRoutes:
        if regRoute.Method == method and regRoute.Regex == regex:
            raise ValueError('Duplicated route: "%s".' % routePath)
    regRoute = _registeredRoute(handler, method, routePath, regex, argNames)
    _registeredRoutes.append(regRoute)


# ============================================================================
# ===( ResolveRoute )=========================================================
# ============================================================================


def ResolveRoute(method, path):
    try:
        path = path.lower()
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        for regRoute in _registeredRoutes:
            if regRoute.Method == method:
                reMatch = regRoute.Regex.match(path)
                if reMatch:
                    if not regRoute.ArgNames:
                        return RouteResult(regRoute)
                    args = {}
                    for i, argName in enumerate(regRoute.ArgNames):
                        argValue = reMatch.group(i + 1)
                        try:
                            argValue = int(argValue)
                        except Exception as e:
                            sys.print_exception(e)
                        args[argName] = argValue
                    return RouteResult(regRoute, args)
    except Exception as e:
        sys.print_exception(e)
    return None


# ============================================================================
# ===( RouteResult )==========================================================
# ============================================================================


class RouteResult:
    def __init__(self, regRoute, args=None):
        self._regRoute = regRoute
        self._args = args

    def __repr__(self):
        return "%s %s" % (self._regRoute.Method, self._regRoute.RoutePath)

    @property
    def Handler(self):
        return self._regRoute.Handler

    @property
    def Method(self):
        return self._regRoute.Method

    @property
    def RoutePath(self):
        return self._regRoute.RoutePath

    @property
    def Args(self):
        return self._args


# ============================================================================
# ===( Methods )==============================================================
# ============================================================================

# MicroPython 1.12 doesn't have the enum module introduced in Python 3.4.
class HttpMethod:
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


# ============================================================================
# ===( Private registered routes  )===========================================
# ============================================================================

_registeredRoutes = []

# ------------------------------------------------------------------------


class _registeredRoute:
    def __init__(self, handler, method, routePath, regex, argNames):
        self.Handler = handler
        self.Method = method
        self.RoutePath = routePath
        self.Regex = regex
        self.ArgNames = argNames


# ============================================================================
# ============================================================================
# ============================================================================