var _crudApiPrefixes = {}

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
      paramsSTR = urlslice(0, url.length-1);
    }
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
  if (method == "GET" || method == "HEAD") { url = eziBuildGETParams(data, pkInURL); }

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
  request.send(data);
}

function eziGETModel(app, model, params, successCallback, apiName="default", failureCallback=function(){}) {
  urlPrefix = _crudApiPrefixes[app][apiName].url + model.toLowerCase();
  pkInURL = _crudApiPrefixes[app][apiName].pkInURL;
  eziAjaxCall(urlPrefix, successCallback, data=params, failureCallback=failureCallback, pkInURL=pkInURL)
}
