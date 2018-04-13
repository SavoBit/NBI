# [NBI - Orchestration Service]

Orchestration service provides topological information to the GUI, through this API the GUI can query active
End to End Services (E2ES), services with associated APPs and even for each APP the virtual resources instantiated.

## Installation

The NBI Orchestration service contains a Dockerfile, that makes the usage of the service simple.

First the user creates the docker image

```sh
$ docker build -t image_name .
```

Then the user runs the created image

```sh
$ docker run -itd --net host image_name
```

### Requirements

This project requires the Falcon framework as the WSGI framework, Gunicorn to run the WSGI APP, the keystone module to
authorize the requests. The requirements are already installed on the Docker container.

Other requirements are listed on the requirements.txt file.

## Configuration

To configure the Catalogue service three files must be used:

- Dockerfile, which contains the GUNICORN BIND variable and the INVENTORY_URL to connect to the service inventory.
- wsgi.ini, with the keystone middleware configurations
- conf.ini, to configure GUNICORN, LOGGING and TOPOLOGY_DATABASE to connect NBI to the topology manager

## Usage

After configuring the service, starting the docker container and having keystone and the identity service running, the
user will have a REST API that can be used to collect inventory information, topology data and orchestration actions.
The Keystone and identity service are only used to acquire an authentication token. To use this correctly the user must
have the conf.ini file correctly configured with its services and databases running.

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

