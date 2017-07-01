# ezi
API development framework

Easily create Rest APIs for your Django models or other APIs that return JSON text. The API is highly customizable allowing you to alter its behavior to your satisfaction.

## Dependancies
Django 1.7 or later

## Installing ezi
In your virtual environment, run

```pip install git+git://github.com/ianbro/ezi.git```

## Getting Started

### Basic JSON API
If you want to customize your own JSON API using ezi, all you have to do is use class based views for your
API views and extend ezi.views.ApiView.

```
from ezi.views import ApiView

class MyJsonApiView(ApiView):

    allowed_methods = ("POST", "GET")
```

For information on allowed_methods, see https://github.com/ianbro/ezi/blob/master/CLASS_DOCUMENTATION.md.

From here, its simple to implement. For each verb allowed in allowed_methods, create the corresponding method.

```
from django.http import JsonResponse

from ezi.views import ApiView

class MyJsonApiView(ApiView):

  allowed_methods = ("POST", "PUT")

  def put(self, request, *args, **kwargs):
    return JsonResponse({"success": True})

  def post(self, request, *args, **kwargs):
    return JsonResponse({"success": True})

  # No need to add get or delete method as any requests of this type will not be allowed.
```

Please note that the only thing that is ezi framework specific is the use of allowed_methods. your view do not need to do anything specific. Treat them as if you were simply writing a view for django's View class.

Also, because ApiView extends View, any verb that you want to make a request to must have the corresponding method implemented. So if you want to be able to make a GET request, you must implement the get method as well as add "GET" to the list of allowed_methods.

### Rest API
Create a simple REST API for your Django models by simply extending a View class and hooking it up to a URL.

```
from ezi.views import ModelCrudApiView

class MyModelCrudApiView(ModelCrudApiView):

    model = MyModel

    allowed_methods = ("POST", "GET", "PUT", "DELETE")
```

For the default behavior, not implementation of the verb methods is needed. ModelCrudApiView implementats these method with default behavior.

If needed, the verb methods (get, post, put, delete) can be overriden to do what you want. The basic functionality that these methods do are contained and available in methods contained in ModelCrudApiView. For information on these, see https://github.com/ianbro/ezi/blob/master/CLASS_DOCUMENTATION.md.

```
from django.http import JsonResponse

from ezi.views import ModelCrudApiView

class MyModelCrudApiView(ModelCrudApiView):

    model = MyModel

    allowed_methods = ("POST", "GET", "PUT", "DELETE")

    def delete(self, request, *args, **kwargs):
      # Override delete in super class.
      return JsonResponse({"success": True})

    # get, post and put will still utilize the default implementation.
```

In order for the ModelCrudApiView to work properly, the url must provide a url parameter named pk. This must be a url parameter contained in the url regex. If it is in the GET parameters or the data payload (such as request.POST), it will not be processed and GET, PUT, and DELETE requests won't work. POST requests do not require a pk parameter.

allowed_methods for this class serves the same purpose as that in ApiView. Note that ModelCrudApiView extends ApiView.
