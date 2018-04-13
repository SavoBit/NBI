# [Keystone Service]

This project allows to instantiate keystone alongside the mysql needed to have the project running.

```sh
$ docker-compose up --build
```

By default it's created an admin with the id default
The adminisrtation password can be set through the variable ${ADMIN_PASSWORD}, and by default it has the value admin.

The domain is mapped to a tenant in the SELFNET concept.
