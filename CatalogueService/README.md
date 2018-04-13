# [NBI - Catalogue Service]

Catalogue service gives the needed tools to manage SELFNET APPs, Network Services and E2ES by providing endpoints to
add, update, enable, disable and remove them from the system.

The NBI app catalogue is responsible to proxy the app catalogue providing an interface to the NBI that is able to
abstract it simplifying the work done by the GUI.

## Installation

The NBI catalogue service contains a Dockerfile, that make the usage of the service simple.

First the user creates the docker image

```sh
$ docker build -t image_name .
```

Then the user runs the created image

```sh
$ docker run -itd --net host image_name
```

### Requirements

This project requires the Falcon framework as the WSGI framework, the falcon-multipart to process the uploading file
on the post creating a new APP, Gunicorn to run the WSGI APP, the keystone module to authorize the requests. The
requirements are already installed on the Docker container.

Other requirements are listed on the requirements.txt file.

## Configuration

To configure the Catalogue service three files must be used:

- Dockerfile, which contains the GUNICORN BIND variable
- wsgi.ini, with the keystone middleware configurations
- conf.ini, to configure GUNICORN, LOGGING and the APP_CATALOGUE URL

## Usage

After configuring the service, starting the docker container and having keystone and the identity service running, the
user will have a REST API that can be used to manage the catalogue service. The Keystone and identity service are only
used to acquire an authentication token. To use this correctly the user must have the APP catalogue configured and
running.

To obtain a session token:

```sh
curl -X POST \
  http://0.0.0.0:7000/nbi/auth/api/login \
  -H 'content-type: application/json' \
  -d '{
  "auth": {
    "username": "username",
    "password": "password",
    "tenant": "tenant"
  }
}'
```

There's a yaml file containing an OpenAPI Specification that can be used on swagger to test the service. It's only
needed the keystone installation and identity service running both also available in the NBI project, as Dockerfiles.
