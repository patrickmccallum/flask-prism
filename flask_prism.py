from functools import wraps
import inspect
import json

from flask import Response, current_app, request
from werkzeug.wrappers import Response as ResponseBase

__all__ = ('ReturnableResponse', 'Prism', 'ResponseMapper')

class ReturnableResponse(Response):
    STATUS_OK = 200
    DEFAULT_MIMETYPE = 'text/json'

    PRISM_VERSION_ATTRIBUTE = 'prism_version'
    PRISM_MIMETYPE_ATTRIBUTE = 'prism_mimetype'

    def __init__(self, objects, status=STATUS_OK, as_list=False, mimetype=None, version=None):
        super(ReturnableResponse, self).__init__()
        if isinstance(objects, list):
            self.data_objects = objects
        else:
            self.data_objects = [objects]

        self.as_list = as_list

        # Get mimetype from representations
        mimetype_model_rep = self.get_mimetype_representation()
        if mimetype_model_rep != None:
            self.mimetype = mimetype_model_rep

        # If mimetype is defined in this response then override
        if mimetype != None:
            self.mimetype = mimetype

        self.response = self.build_response()

        if isinstance(status, (int, )):
            self.status_code = status
        else:
            self.status = status

        self.mimetype = ReturnableResponse.DEFAULT_MIMETYPE if mimetype_model_rep == None else self.mimetype

    def get_mimetype_representation(self):

        for o in self.data_objects:
            func = self.get_representation_builder(o)

            if hasattr(func, ReturnableResponse.PRISM_MIMETYPE_ATTRIBUTE):
                return getattr(func, ReturnableResponse.PRISM_MIMETYPE_ATTRIBUTE)

        return None

    def get_representation_builder(self, object, soft_fail=False):
        # Get class name of object
        class_name = object.__class__.__name__

        # Determine if a blueprint is being used
        if request.blueprint != None:
            # Get BP from current app
            bp = current_app.blueprints[request.blueprint]

            # Get prism_version from BP if applicable
            version = getattr(bp, ReturnableResponse.PRISM_VERSION_ATTRIBUTE) \
                if hasattr(bp, ReturnableResponse.PRISM_VERSION_ATTRIBUTE) else None
        else:
            version = None

        # Get representation
        func = current_app.ext_prism.lookup_mappings(class_name, version=version)

        if func is None:
            if not soft_fail:
                raise Exception('Issue retrieving stored function reference for PRISM mapping on %s object. '
                                'Does this object have an api_response/is the right version defined?' % class_name)

        return func

    def get_representation_dict(self, object):
        # Get response from builder
        resp = self.get_representation_builder(object)(object)

        # Look for has_ methods and evaluate
        def evaluate_level(items):
            # TODO:// Convert and combine, this if statement is poor.
            if isinstance(items, dict):
                for k, v in items.items():
                    if isinstance(v, (dict, list)):
                        # If a dict or a list pass through eval_level again for further processing
                        evaluate_level(v)
                    elif isinstance(v, ResponseEvaluator.Killer):
                        # If killer object, pop this key (I doubt this will ever be hit, but just for safety)
                        items.pop(k, 0)
                    elif isinstance(v, ResponseEvaluator):
                        # If a response evaluator, evaluate
                        new_val = v.evaluate_for_response(object)

                        # If new_val is a Killer, pop this key and continue
                        if isinstance(new_val, ResponseEvaluator.Killer):
                            items.pop(k, 0)
                            continue

                        # If new_val is a list or dict, pass through eval_level again for further processing
                        if isinstance(new_val, (dict, list)):
                            evaluate_level(new_val)

                        items[k] = new_val
                    elif self.get_representation_builder(v, soft_fail=True) is not None:
                        new_val = self.get_representation_dict(v)

                        items[k] = new_val

            elif isinstance(items, list):
                for i, v in enumerate(items):
                    if isinstance(v, (dict, list)):
                        # If a dict or list pass through eval_level again for further processing
                        evaluate_level(v)
                    elif isinstance(v, ResponseEvaluator.Killer):
                        # If a killer object, remove this item from the list
                        items.remove(v)
                    elif isinstance(v, ResponseEvaluator):
                        # If it's a response evaluator, evaluate it
                        new_val = v.evaluate_for_response(object)

                        # If new_val is a Killer, remove this value and continue
                        if isinstance(new_val, ResponseEvaluator.Killer):
                            items.remove(v)
                            continue

                        # If new_val is a list or dict, pass through eval_level again for further processing
                        if isinstance(new_val, (dict, list)):
                            evaluate_level(new_val)

                        items[i] = new_val

                    elif self.get_representation_builder(v, soft_fail=True) is not None:
                        new_val = self.get_representation_dict(v)

                        items[i] = new_val

            return items

        final = evaluate_level(resp)

        return final

    def build_response(self):
        return_objects = {} if not self.as_list and self.data_objects.__len__() <= 1 else []

        if self.data_objects.__len__() > 1:
            for o in self.data_objects:
                return_objects.append(self.get_representation_dict(o))

        elif self.data_objects.__len__() == 1:
            r = self.get_representation_dict(self.data_objects[0])

            if self.as_list:
                return_objects.append(r)
            else:
                return_objects = r

        return json.dumps(return_objects)


class Prism(object):
    def __init__(self, app=None):
        self.app = app
        self.mapper = ResponseMapper()

        if app is not None:
            app.ext_prism = self

    def init_app(self, app):
        self.app = app
        app.ext_prism = self

    def get_calling_class_name(self):
        stack = inspect.stack()
        the_class = str(stack[2][0].f_locals["self"].__class__).split('.')[1]
        return the_class


    def has_or_none(self, key, value, version=None):
        r = ResponseEvaluator(self, '%s' % (self.get_calling_class_name()), key, ResponseEvaluator.MODE_NONE, value, version=version)

        return r

    def has_or_exclude(self, key, value, version=None):
        r = ResponseEvaluator(self, self.get_calling_class_name(), key, ResponseEvaluator.MODE_EXCLUDE, value, version=version)

        return r

    def has_or_else(self, key, value, else_value, version=None):
        r = ResponseEvaluator(self, self.get_calling_class_name(), key, ResponseEvaluator.MODE_ELSE, value, version=version)
        r.alternative = else_value

        return r

    def api_representation(self, version=None, mimetype=None):
        """
        :param version: The version of this representation as an integer
        :param mimetype: The final mimetype of this response, default is text/json
        """

        def func_decorator(func):
            @wraps(func)
            def process(*args, **kwargs):
                return func(*args, **kwargs)

            # Determine if method was used in a class or not
            frames = inspect.stack()
            defined_in_class = False
            first_statment = ''
            if len(frames) > 2:
                maybe_class_frame = frames[2]
                statement_list = maybe_class_frame[4]
                first_statment = statement_list[0]
                if first_statment.strip().startswith('class '):
                    defined_in_class = True

            if not defined_in_class:
                raise Exception('PRISM representation methods must be defined in a class.')

            # Get class name for use
            class_name = first_statment.replace('class ', '').split('(')[0]

            # Store mimetype to function
            func.prism_mimetype = mimetype

            # Map the method to a format we know about
            self.mapper.map('%s/%s/rep/%s' % (class_name, version, func.__name__), func)

            return process

        return func_decorator

    def has_access(self, version=None):
        def func_decorator(func):
            @wraps(func)
            def process(*args, **kwargs):
                return func(*args, **kwargs)
            # FIXME:// Is having two copies of this code required? It could easily be moved into a method.
            # Determine if method was used in a class or not
            frames = inspect.stack()
            defined_in_class = False
            first_statment = ''
            if len(frames) > 2:
                maybe_class_frame = frames[2]
                statement_list = maybe_class_frame[4]
                first_statment = statement_list[0]
                if first_statment.strip().startswith('class '):
                    defined_in_class = True

            if not defined_in_class:
                raise Exception('PRISM access methods must be defined in a class.')

            # Get class name for use
            class_name = first_statment.replace('class ', '').split('(')[0]

            # Map the method to a format we know about
            self.mapper.map('%s/%s/acc/%s' % (class_name, version, func.__name__), func)

            return process

        return func_decorator

    def check_has_access(self, instance, access_reference, access_key, version=None):
        # Get the relevant access method
        func = self.lookup_mappings(class_name=access_reference, version=version, type='acc')

        # If result is none, raise exception
        if func is None:
            raise Exception('Mapping not found for class %s, version %s, would have used access key %s' % (access_reference, version, access_key))

        # Get the result from method
        result = func(instance, access_key)

        # If the user wrote a function that doesn't return a boolean, the returned value is useless to us. Fail now.
        if not isinstance(result, bool):
            raise Exception('PRISM issue checking for access, expected boolean but got %s' % type(result))

        # Return the result
        return result

    def __get_mapper(self):
        return self.mapper

    def lookup_mappings(self, class_name, version=None, type='rep'):
        return self.mapper.return_for(class_name=class_name, version=version, type=type)

class ResponseEvaluator(object):
    """
    An instance of this class is inserted in place of values when using prisms has_ methods. It is evaluated on the way
    out and the value replaced.
    """

    MODE_NONE = 0
    MODE_EXCLUDE = 1
    MODE_ELSE = 2

    def __init__(self, prism, access_reference, access_key, mode, value, version=None):
        self.mode = mode
        self.prism = prism
        self.access_reference = access_reference
        self.access_key = access_key
        self.value = value
        self.version = version

        self.alternative = None

    def get_alternative(self):
        # Get alternative if mode is None
        if self.mode == ResponseEvaluator.MODE_NONE:
            return None
        # Get alternative if mode is Exclude
        elif self.mode == ResponseEvaluator.MODE_EXCLUDE:
            return ResponseEvaluator.Killer()
        # Get alternative if mode is Else
        elif self.mode == ResponseEvaluator.MODE_ELSE:
            return self.alternative
        # Raise exception if unknown constant
        else:
            raise Exception("Unrecognised mode for Response evaluator. Expected known constant, given %s" % self.mode)

    def evaluate_for_response(self, instance):
        # Return the positive value if has_access check is passed, else the alternative
        return self.value \
            if self.prism.check_has_access(instance, self.access_reference, self.access_key, version=self.version) \
            else self.get_alternative()

    # Shelf class to know if we should kill off this value or key/value
    class Killer(object):
        pass


class ResponseMapper(object):
    """
    This class maintains references to representations for objects.
    """

    def __init__(self):
        self.maps = {}

    def map(self, key, response):
        if key in self.maps.keys():
            raise Exception('Map key "%s" overwrites existing mapping. Try renaming the new method and try again.' %
                            key)

        self.maps[key] = response

    def return_for(self, class_name, version, type):
        for key, function in self.maps.items():
            if key.startswith('%s/%s/%s' % (class_name, version, type)):
                return function

        return None
