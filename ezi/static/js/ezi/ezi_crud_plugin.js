var _crudApiPrefixes = {}

/**
Returns the value of the cookie with the given name. I am specifically using
this to get the csrftoken.
*/
function _getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
Creates an entry in _api_prefixes that maps an app name to an API prefix. This
prefix should include the url starting after the domain and ending at the base
url for all api endpoints in the registered api.

These prefixes will be used by eziCallModel and other ezi js remotes to get the
correct api.

parameters:
  appName: The app that this api will be for. This will be used to get the
  correct app for the api.

  apiName: The name of the api in the app. This is incase there are multiple
  api's in the given app. If no apiName is given, it will default to "default".

  prefix: The prefix of the api. This will be used to generate the url when
  calling to a specified api.

The value of each entry will have the prefix and whether or not the url contains
a pk in the url as an optional argument.
*/
function eziRegisterCRUDApi(appName, prefix, apiName="default", pkInURL=false) {
  _crudApiPrefixes[appName] = {};
  _crudApiPrefixes[appName][apiName] = {
    url: prefix,
    pkInURL: pkInURL
  }
}

/**
Builds the string representation of the parameters that are to be sent to the
url in the GET arguments. This will be the string that can be appended to the
url. This string includes the "?" at the beginning of the string.

if pkInURL is true, then the parameter called pk or id will be added at the end
of the pure url (before the "?") instead of as a GET parameter.
*/
function eziBuildGETParams(data, pkInURL=false) {
  if (data) {
    paramsSTR = "?";
    for (key in data) {
      if ((key == "pk::int" || key == "id::int") && pkInURL) {
        paramsSTR = data[key].toString() + paramsSTR;
      } else {
        paramsSTR = paramsSTR + key + "=" + data[key] + "&";
      }
    }

    // Remove the last character which will be an & if any params were added.
    if (Object.keys(data).length) {
      paramsSTR = paramsSTR.slice(0, paramsSTR.length-1);
    }

    return paramsSTR
  } else {
    return "";
  }
}

function eziBuildRequestPayload(data, pkInURL=false) {
  if (data) {
    payload = "";

    for (key in data) {
      if (key == "pk::int" && pkInURL) {
        // Don't add it to the payload.
      } else {
        payload = payload + "[" + key + "]:=:[" + data[key] + "]\n";
      }
    }

    // Remove the last character which will be an & if any params were added.
    if (Object.keys(data).length) {
      payload = payload.slice(0, payload.length-1);
    }

    return payload;
  } else {
    return "";
  }
}

/**
Sends an asycronous request (AJAX) to the given url using the given method.
When the request finishes, if it was successful (status code of 200), then the
successCallback function will be called. Otherwise, the failureCallback function
will be called.
*/
function eziAjaxCall(url, successCallback, method="GET", data={}, failureCallback=function(){}, pkInURL=false) {
  var payload = null;
  if (method == "GET" || method == "HEAD") { url = url + eziBuildGETParams(data, pkInURL); }
  else {
    if (pkInURL && "pk::int" in data) {
      url = url + data["pk::int"].toString() + "/";
    }
    payload = eziBuildRequestPayload(data, pkInURL);
  }

  request = new XMLHttpRequest();
  request.onreadystatechange = function() {
    if (this.readyState == 4) {
      if (this.status == 200) {
        successCallback();
      } else if (this.status == 500 || this.status == 400 || this.status == 404) {
        failureCallback();
      }
    }
  }

  request.open(method, url, true);
  request.setRequestHeader("X-CSRFToken", _getCookie("csrftoken"));
  console.log(method);
  console.log(data);
  console.log(payload);
  request.send(payload);
}

/**
Returns a list of objects in the database from the api that match the given
parameters.

Parameters:
  app: name of the app that the api belongs to. This is used to fetch the url.
  model: name of the model in the app that this api call will fetch. This is
          used to fetch the url.
  params: list of parameters to send in the api call.
  apiName: name of the api in the app that this call belongs to. THis is used to
          fetch the url.
  successCallback: function that will be called after the api call returns with
          a status code of 200.
  failureCallback: function that will be called after the api call returns with
          a status code that is not 200.
*/
function eziGETModel(app, model, params, successCallback, apiName="default", failureCallback=function(){}) {
  urlPrefix = _crudApiPrefixes[app][apiName].url + model.toLowerCase() + "/";
  pkInURL = _crudApiPrefixes[app][apiName].pkInURL;
  eziAjaxCall(urlPrefix, successCallback, "GET", data=params, failureCallback=failureCallback, pkInURL=pkInURL)
}

/**
Makes a PUT call to a crud api that will create an instance of the given model
with the given values in params.

Parameters:
  app: name of the app that the api belongs to. This is used to fetch the url.
  model: name of the model in the app that this api call will instantiate. This
          is used to fetch the url.
  params: list of parameters to send in the api call.
  apiName: name of the api in the app that this call belongs to. THis is used to
          fetch the url.
  successCallback: function that will be called after the api call returns with
          a status code of 200.
  failureCallback: function that will be called after the api call returns with
          a status code that is not 200.

NOTE: The csrf token is not needed in params. It is automatically retreived from
the cookies.
*/
function eziInstantiateModel(app, model, params, successCallback, apiName="default", failureCallback=function(){}) {
  urlPrefix = _crudApiPrefixes[app][apiName].url + model.toLowerCase() + "/";
  pkInURL = _crudApiPrefixes[app][apiName].pkInURL;
  params.csrfmiddlewaretoken = _getCookie("csrftoken");
  console.log(params);
  eziAjaxCall(urlPrefix, successCallback, "PUT", data=params, failureCallback=failureCallback, pkInURL=pkInURL)
}

/**
Deletes a list of objects in the database using a DELETE call to a specific api
endpoint.

Parameters:
  app: name of the app that the api belongs to. This is used to fetch the url.
  model: name of the model in the app that this api call will fetch to delete.
          This is used to fetch the url.
  params: list of parameters to send in the api call.
  apiName: name of the api in the app that this call belongs to. THis is used to
          fetch the url.
  successCallback: function that will be called after the api call returns with
          a status code of 200.
  failureCallback: function that will be called after the api call returns with
          a status code that is not 200.

NOTE: The csrf token is not needed in params. It is automatically retreived from
the cookies.
*/
function eziDeleteModelInstance(app, model, params, successCallback, apiName="default", failureCallback=function(){}) {
  urlPrefix = _crudApiPrefixes[app][apiName].url + model.toLowerCase() + "/";
  pkInURL = _crudApiPrefixes[app][apiName].pkInURL;
  params.csrfmiddlewaretoken = _getCookie("csrftoken");
  console.log(params);
  eziAjaxCall(urlPrefix, successCallback, "DELETE", data=params, failureCallback=failureCallback, pkInURL=pkInURL)
}
