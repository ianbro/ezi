from django.conf.urls import url

def crud_api_url_factory(models, url_prefix="api/crud/"):
    """
    Generates urls for the given model classes in models. The urls will be
    in the format "{url_prefix}{model_name}{id(*optional*)}" where:

        url_prefix is the value in the parameter "url_prefix",
        model_name is the simple, lowercase name of each model class in the
            parameter "models",
        id is an optional regular expression that holds a url parameter as an
            int called pk.

    url_prefix can be customized by passing a different valid url string into
    the "url_prefix" keyword argument. By default, url_prefix is "api/crud/".

    For example, if a model class is called "Person" and the url_prefix has
    a value of "api/", then the url will be:

        "api/person/(?:(?P<pk>\d+))?"

    Each url points to a view specified in its corresponding model class. The
    view will be retreived from a class variable in the model class called
    "crud_api_view". For example:

        from .views import PersonCrudApiView

        class Person(models.Model):
            # fields...

            crud_api_view = views.PersonCrudApiView.as_view()

    The name of the url used or dynamic url referencing will be the same as the
    url itself but with all forward slashes replaced by underscores. So if the
    url is "api/crud/person", then the url name will be "api_crud_person".

    Parameters:

        models: list of classes. These classes must contain a class variable
            called crud_api_view.

        url_prefix: string to go in front of the model name in the url.
    """
    def generate_url(cls_model_class):
        return url(
            r'{prefix}{model_name}(?:(?P<pk>\d+))?'.format(
                **{
                    "prefix": url_prefix,
                    "model_name": cls_model_class.__name__.lower()
                }
            ),
            cls_model_class.crud_api_view().as_view(),
            name = "{prefix}_{model_name}".format(
                **{
                    "prefix": url_prefix.replace("/", "_"),
                    "model_name": cls_model_class.__name__.lower()
                }
            )
        )

    return [generate_url(model) for model in models
            if hasattr(model, "crud_api_view") and not model.crud_api_view is None]
