# [NBI]

The API broker sublayer is composed of three sub-models, (i) Requested
information, (ii) Authentication and Authorization and, (iii) Real Time events. The

Requested information is based on REpresentational State Transfer (REST) micro-
services that abstract the communication between SELFNET users and SELFNET bottom layers.
This abstraction allows the protection of SELFNET’s bottom layers,
since the user can’t access them directly and don’t know which services rely
underneath of it. This module is responsible to request, process and merge data from
multiple components and send it back to the GUI, via its own REST API independent
from SON Autonomic Layer services.

The main responsability of the API broker is to intermediate the access to multiple source of
information. Most of that information is requested by the GUI in order to display it to
an end user providing the means to analyse a given set of data. This module is responsible to
receive these requests and through the correct API collect the data, organize it and return it to the
requester, the GUI.

Authentication and Authorization is the term applied for controlling the access to resources.
This process ensures that the available resources are only provided to users that respect the
requirements to access them. The process is divided in two steps, authentication and authorization.
Authentication comprises the steps taken to identify a user. This process ensures the
user is who it claims to be. A common method of authentication asks each user to
provide a unique username and a password. The password must be private and only
known by the user, ensuring this way that no one should be capable of stealing the
user’s identity.

A real time module is a component that allows SELFNET access layer to handle real
time events. Using this feature, SELFNET GUI is able to provide feedback to the user
regarding events that are happening in the infrastructure, without the need to query
those events, e.g., it can provide real time updates to the topology, or even show
enforced actions as they are happening within the infrastructure, allowing the user to
have a fast evaluation of what occurs in the networks.

## Installation

All NBI components are available through a docker image. This way it's possible to ease the
installation and integration process it's only needed to configure each service and have the 
needed SELFNET information sources to be collected by each NBI service. 

### Requirements

The only requirement needed to have the NBI services running is having docker, since every service
can be built as a Docker image and running within a container.

## Configuration

Every NBI API service is composed by three configuration files:

- Dockerfile, which controls the docker image that will be generated
- wsgi.ini, containing authentication information
- conf.ini, specific service configurations

## Usage

It's advisable to use every NBI service behind a proxy, this way, it's possible to
have all services being serve from the same port.

## License

The SELFNET-NBI is published under Apache 2.0 license. Please see the LICENSE file for more details.
