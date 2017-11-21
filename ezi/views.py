from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from utils import (IanmannJsonResponse,
                    respond_bad_request_verb,
                    get_params_to_queryset_kwargs,
                    valid_method,
                    respond_list_deleted,
                    respond_success_no_results_to_return)

class ApiView(View):
    """
    Provides commonly used functionality for api views. This includes things
    such as validation of requests and other things.

    Fields:

        allowed_methods - tuple of strings
            List of verbs that this view can accept. Any requests made for this view
            must be made with a method contained in this list.

            For example, if this list only contains "PUT" and "GET" but the request was
            made with a "POST" verb, then that request should not be processed.

            The possible verbs for this are POST, GET, PUT, and DELETE
    """

    allowed_methods = ()

    _payload = {}
    @property
    def payload(self):
        if not self._payload:
            data = {}
            payload = self.request.read()

            if not payload: return {}

            payload_list = payload.split("\n")
            for argument in payload_list:
                key_val = argument.split("]:=:[")
                key = key_val[0][1:]
                val = key_val[1][:-1]
                data[key] = val

            self._payload = data

        return self._payload

    def dispatch(self, request, *args, **kwargs):
        """
        Override of the super classes dispatch.
        This implementation of dispatch validates the method of the request.

        If the method verb is not allowed for this view based on the
        allowed_methods, then the 400 error in respond_bad_request_verb is
        returned and the view does not go any further than this method. This
        way, requests with verbs that are not allowed are not processed.
        """
        if not self.valid_method():
            return respond_bad_request_verb(self.request)
        else:
            return super(ApiView, self).dispatch(request, *args, **kwargs)

    def get_params_to_queryset_kwargs(self, verb=None):
        """
        Each parameter is wrapped in a RestApiGetParameter
        object and parsed and validated in the instantiation method for that
        object. Then they are used in the filter that will return the queryset
        of model objects.

        This method acheives that and returns the parameters as a key_value pair
        that can be sent to a queryset.

        This will get parameters from the request body unless the verb is GET.
        In this case, the parameters will be grabbed from the url parameters in
        self.request.GET.

        verb must be one of "GET", "PUT", "POST" or DELETE.

        NOTE: This uses the method implementation that is in this module outside
        of this class. This is not recursion; the method it is calling just has
        the same name. This method just acts as a wrapper for that.
        """
        if verb == "GET" or verb == "HEAD": data = self.request.GET
        else:
            data = {}
            for key, val in self.payload.items():
                if "::" in key and len(key.split("::")) == 2:
                    data[key] = val
        return get_params_to_queryset_kwargs(data)

    def valid_method(self):
        """
        Simple wrapper for calling valid_method from this module, sending it
        self.request and self.allowed_methods by default.
        """
        return valid_method(self.request, self.allowed_methods)

class ModelCrudApiView(ApiView):
    """
    Provides default implementation of the get, post, put and delete methods.
    This allows extremely easy configuration and setup for a REST API that
    provides CRUD operations on a model.

    Some examples of how this helps is in creating and viewing model objects.
    In order to allow this, you simply add GET and PUT to the list of
    allowed_methods. The methods that are called in these cases (get() and
    put()) already implement creation and viewing by default so no logic is
    needed.

    Fields:

        model - class object; must extend Model:
            The Model class on which the CRUD operations will be applied.

        instance_pk - int
            The Primary Key for the instance for which certain CRUD operations
            will be applied. This is only needed on GET and DELETE because these
            are the only methods that use a single active instance. PUT will
            ignore this field by default.
    """

    model = None

    instance_pk = 0

    def dispatch(self, request, *args, **kwargs):
        """
        Override of the super classes dispatch.
        This implementation simply gets the pk from the url parameters and sets
        it to the attribute instance_pk.

        If no pk is supplied to the url, then the attribute instance_pk defaults
        to 0.

        This is optional because the request may be trying to create a new
        object, not retreive an existing one. In that case, a pk would not be
        sent to the url parameters.


        TODO: May have to move csrf token input from request.PUT and
        DELETE. It is not in the right format to be parsed by the method that
        parses RestApiGetParameter objects so it will cause errors for that.
        """
        self.instance_pk = int(kwargs.get("pk", 0) or 0)
        return super(ModelCrudApiView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        """
        Retreives the object from the database that is of the type designated by
        self.model and has the id of self.instance_pk.

        If no object with those conditions is found, then a 404 error is thrown.
        """
        try:
            return self.get_object_list().get(pk=self.instance_pk)
        except self.model.DoesNotExist:
            raise Http404("Object not found with a primary key of: {} and the given GET parameters.".format(self.instance_pk))

    def get_object_json(self):
        """
        Simply gets the views object using self.get_object and returns its
        implementation of the json method.
        """
        return self.get_object().json()

    def get_object_list(self):
        """
        Returns a list of objects that are of the type denoted in self.model.
        The objects returned will be those that fulfill the parameters in the
        urls GET parameters.
        """
        kwargs_for_filter = self.get_params_to_queryset_kwargs("GET")

        return self.model.objects.filter(**kwargs_for_filter)

    def get_object_list_json(self):
        """
        Returns a list of objects of the type denoted in self.model. Those
        objects are returned in this method in json format according to the json
        method on their model class.

        This method uses self.get_object_list to get the list of objects.
        """
        return [x.json() for x in self.get_object_list()]

    def create_object(self):
        """
        Creates an instance of self.model using the values supplied in the PUT
        data payload.
        """
        instantiation_params = self.get_params_to_queryset_kwargs("PUT")

        return self.model.objects.create(**instantiation_params)

    def delete_object(self):
        """
        Deletes the object from the database that is of the type designated by
        self.model and has the id of self.instance_pk.

        If no object with those conditions is found, then a 404 error is thrown.
        """
        instance = get_object_or_404(self.model, pk=self.instance_pk)
        instance.delete()

    def delete_object_list(self):
        """
        Deletes a list of objects that are of the type denoted in self.model.
        The objects deleted will be those that fulfill the parameters in the
        urls GET parameters.

        Returns the number of items deleted.
        """
        kwargs_for_filter = self.get_params_to_queryset_kwargs("DELETE")

        objects_to_delete = self.model.objects.filter(**kwargs_for_filter)
        count = objects_to_delete.count()
        objects_to_delete.delete()

        return count

    def put(self, request, *args, **kwargs):
        """Creates an object and returns the resulting object in json format."""
        return IanmannJsonResponse(self.create_object().json())

    def get(self, request, *args, **kwargs):
        """
        Returns either a list of objects or a single object based on the format
        of the url.

        If the url has a value set for the pk url parameter, then
        this view will assume the request is asking for a single entity.

        Otherwise, this view will assume the request is asking for a list of
        entities.

        The parameters sent to the model filter will be retreived
        from the url GET parameters. These parameters will be wrapped in
        RestApiGetParameter object so this means that all GET parameters must
        be in a valid format to be parsed by that class.
        """
        if self.instance_pk and self.instance_pk > 0:
            return IanmannJsonResponse(self.get_object_json())
        else:
            return IanmannJsonResponse(self.get_object_list_json())

    def delete(self, request, *args, **kwargs):
        """
        Deletes either a list of objects or a single object based on the format
        of the url.

        If the url has a value set for the pk url parameter, then
        this view will assume the request is asking to delete a single entity.

        Otherwise, this view will assume the request is deleting a list of
        entities.

        The parameters sent to the model filter will be retreived
        from the parameters in the data payload. These parameters will be
        wrapped in RestApiGetParameter object so this means that all parameters
        must be in a valid format to be parsed by that class.
        """
        if self.instance_pk and self.instance_pk > 0:
            self.delete_object()
            return respond_success_no_results_to_return("deleted")
        else:
            num_deleted = self.delete_object_list()
            return respond_list_deleted(num_deleted)


def model_crud_api_view_factory(model_class):
    """
    Returns a class based view that contains default behavior for the ezi view
    ModelCrudApiView. This view is applied to the model_class and its __name__
    is "{model_name}CrudApiView" where {model_name} is the model classes name.

    The allowed_methods in this view are GET, POST, PUT and DELETE.
    The model attribute for this view is the class in the parameter model_class.
    """
    class ApiView(ModelCrudApiView):
        model = model_class
        allowed_methods = ("GET", "PUT", "DELETE")

    ApiView.__name__ = "{model_name}CrudApiView".format(model_name=type(model_class).__name__)

    return ApiView
