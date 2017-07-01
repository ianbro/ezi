# Class documentation

## ezi.views.ApiView methods and attributes

Extends django.views.generic.View

Provides commonly used functionality for api views. This includes things
such as validation of requests and other things.

### allowed_methods - tuple of strings
List of verbs that this view can accept. Any requests made for this view
must be made with a method contained in this list.

For example, if this list only contains "PUT" and "GET" but the request was
made with a "POST" verb, then that request should not be processed.

The possible verbs for this are POST, GET, PUT, and DELETE

### dispatch(self, request, *args, **kwargs)
Override of the super classes dispatch.
This implementation of dispatch validates the method of the request.

If the method verb is not allowed for this view based on the
allowed_methods, then the 400 error in respond_bad_request_verb is
returned and the view does not go any further than this method. This
way, requests with verbs that are not allowed are not processed.

### get_params_to_queryset_kwargs(self, verb=None)
Each parameter is wrapped in a ezi.utils.RestApiGetParameter
object and parsed and validated in the instantiation method for that
object. Then they are used in the filter that will return the queryset
of model objects.

This method acheives that and returns the parameters as a key_value pair
that can be sent to a queryset.

This will get parameters from GET, PUT, POST or DELETE. The one that it
gets them from is decided by verb. It defaults to self.request.method.

verb must be one of "GET", "PUT", "POST" or "DELETE".

### valid_method(self)
Searches allowed_methods to see if request.method is in the list. If so,
then the request is permitted to use this method. Otherwise, it is assumed
that the request should not be allowed.

Returns True if the request uses a valid verb. False otherwise

NOTE: This method simply calls ezi.utils.valid_method. This is just an
instance method wrapper for that function.

## ezi.views.ModelCrudApiView methods and attributes

Extends ezi.views.ApiView

Provides default implementation of the get, post, put and delete methods.
This allows extremely easy configuration and setup for a REST API that
provides CRUD operations on a model.

Some examples of how this helps is in creating and viewing model objects.
In order to allow this, you simply add GET and PUT to the list of
allowed_methods. The methods that are called in these cases (get() and
put()) already implement creation and viewing by default so no logic is
needed.

### model - class object; must extend Model:
The Model class on which the CRUD operations will be applied. This model must provide each object with a method called json. The signature for this is as follows:

```
def json(self):
  return {...}
```

This method should be used to return a dictionary representation of each object. This dictionary must be serializable by the django.http.JsonResponse class.

### instance_pk - int
The Primary Key for the instance for which certain CRUD operations
will be applied. This is only needed on GET and DELETE because these
are the only methods that use a single active instance. PUT will
ignore this field by default.

### dispatch(self, request, *args, **kwargs)
Override of the super classes dispatch.
This implementation simply gets the pk from the url parameters and sets
it to the attribute instance_pk.

If no pk is supplied to the url, then the attribute instance_pk defaults
to 0.

This is optional because the request may be trying to create a new
object, not retreive an existing one. In that case, a pk would not be
sent to the url parameters.

### get_object(self)
Retreives the object from the database that is of the type designated by
self.model and has the id of self.instance_pk.

If no object with those conditions is found, then a 404 error is thrown.

### get_object_json(self)
Simply gets the views object using self.get_object and returns its
implementation of the json method.

### get_object_list(self)
Returns a list of objects that are of the type denoted in self.model.
The objects returned will be those that fulfill the parameters in the
urls GET parameters.

### get_object_list_json(self)
Returns a list of objects of the type denoted in self.model. Those
objects are returned in this method in json format according to the json
method on their model class.

This method uses self.get_object_list to get the list of objects.

### create_object(self)
Creates an instance of self.model using the values supplied in the PUT
data payload.

### delete_object(self)
Deletes the object from the database that is of the type designated by
self.model and has the id of self.instance_pk.

If no object with those conditions is found, then a 404 error is thrown.

### delete_object_list(self)
Deletes a list of objects that are of the type denoted in self.model.
The objects deleted will be those that fulfill the parameters in the
urls GET parameters.

Returns the number of items deleted.

### put(self, request, *args, **kwargs)
Creates an object and returns the resulting object in json format.

### get(self, request, *args, **kwargs)
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

### delete(self, request, *args, **kwargs)
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
