# [NBI - Identity Service]

The NBI's Identity service allows SELFNET administrator to manage the tenants available in the system and have full
control over it. It is possible to create, update and delete users in the context of this service, while managing its
roles.

This service implements a proxy to Openstack identity service simplifying some of its concepts and ease its usage
across SELFNET.

This service is the entry point to SELFNET, since it allows users to obtain an authentication token that
grants access to SELFNET.

## Installation

The NBI identity service contains a Dockerfile, that makes the usage of the service simpler.

First the user creates the docker image

```sh
$ docker build -t image_name .
```

Then the user runs the created image

```sh
$ docker run -itd --net host image_name
```

### Requirements

The SELFNET's NBI Identity service only brings added value when running alongside the Openstack's identity service,
Keystone. The service also uses the Keystone Middleware to authenticate incoming requests. The requirements are already
installed on the Docker container.

The NBI Identity service also depends on the Falcon framework as the WSGI framework and Gunicorn to run the WSGI APP.

Other requirements are listed on the requirements.txt file.

## Configuration

To configure the Identity service three files must be used:

- Dockerfile, which contains the GUNICORN BIND variable
- wsgi.ini, with the keystone middleware configurations
- conf.ini, to configure GUNICORN, LOGGING and KEYSTONE access

## Usage

After configuring the service, starting the docker container and having keystone running, the user will have a REST API
that can be used to authenticate users, /nbi/auth, and other to manage the Catalogue services

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

The response will have a X-Subject-Token that must be used in other requests as X-Auth-Token.
E.g., list all users within a Tenant:

curl -X GET \
  http://0.0.0.0:7000/nbi/identity/api/tenants/TENANT_ID/users \
  -H 'x-auth-token: X-SUBJECT-TOKEN'
}'

There's a yaml file containing an OpenAPI Specification that can be used on swagger to test the service. It's only
needed the keystone installation, also available in the NBI project, as Dockerfile.

