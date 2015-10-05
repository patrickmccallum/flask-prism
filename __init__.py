from functools import wraps
import inspect
import json

from flask import Response, current_app
from werkzeug.wrappers import Response as ResponseBase

__all__ = ('ReturnableResponse', 'Prism', 'ResponseMapper')

class ReturnableResponse(Response):
    STATUS_OK = 200
    DEFAULT_MIMETYPE = 'textk/json'

    def __init__(self, objects, status=STATUS_OK, as_list=False, mimetype=DEFAULT_MIMETYPE):
        super(ReturnableResponse, self).__init__()
        if isinstance(objects, list):
            self.data_objects = objects
        else:
            self.data_objects = [objects]

        self.as_list = as_list


        self.response = self.build_response()
        self.status = str(status)
        self.mimetype = mimetype

    def get_representation(self, object):
        class_name = object.__class__.__name__

        func = current_app.ext_prism.lookup_mappings(class_name, version=None)

        if func is None:
            return
        # print "Check it", func(object)

        return func(object)

    def build_response(self):
        return_objects = {} if not self.as_list or self.data_objects.__len__() > 1 else []

        if self.data_objects.__len__() > 1:

            pass
        elif self.data_objects.__len__() == 1:
            self.get_representation(self.data_objects[0])
            return_objects = {}

        return json.dumps(return_objects)


class Prism(object):
    def __init__(self, app):
        self.app = app
        self.mapper = ResponseMapper()

        if app is not None:
            app.ext_prism = self

    def init_app(self, app):
        self.app = app
        app.ext_prism = self

    def api_representation(self, version=None, mimetype=None):
        """
        :param version: The version of this representation as an integer
        """

        def func_decorator(func):
            @wraps(func)
            def process(*args, **kwargs):
                return func(*args, **kwargs)

            frames = inspect.stack()
            defined_in_class = False
            first_statment = ''
            if len(frames) > 2:
                maybe_class_frame = frames[2]
                statement_list = maybe_class_frame[4]
                first_statment = statement_list[0]
                if first_statment.strip().startswith('class '):
                    print first_statment
                    defined_in_class = True

            if not defined_in_class:
                raise Exception('PRISM representation methods must be defined in a class.')

            # Get class name for use
            class_name = first_statment.replace('class ', '').split('(')[0]

            # Map the method to a format we know about
            self.mapper.map('%s/%s/%s' % (class_name, version, func.__name__), func)

            return process

        return func_decorator

    def __get_mapper(self):
        return self.mapper

    def lookup_mappings(self, class_name, version=None):
        return self.mapper.return_for(class_name=class_name, version=version)


class ResponseMapper(object):
    """
    This class maintains references to representations for objects.
    """

    def __init__(self):
        self.maps = {}

    def map(self, key, response):
        print "Mapping %s to" % key, response

        if key in self.maps.keys():
            raise Exception('Map key "%s" overwrites existing mapping. Try renaming the new method and try again.' %
                            key)

        self.maps[key] = response

    def return_for(self, class_name, version):
        for key, function in self.maps.items():
            print "checking %s for %s" % (key, '%s/%s/' % (class_name, version))
            print key.startswith('%s/%s/' % (class_name, version))
            if key.startswith('%s/%s/' % (class_name, version)):
                return function

        return None