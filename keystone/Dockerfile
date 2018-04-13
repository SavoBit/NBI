FROM python:2.7
MAINTAINER Tiago Teixeira "tteixeira@ubiwhere.com"

ENV VERSION=10.0.3

RUN set -x \
    && apt-get -y update \
    && apt-get install -y libffi-dev python-dev libssl-dev mysql-client python-mysqldb \
    && apt-get -y clean

RUN curl -fSL https://github.com/openstack/keystone/archive/${VERSION}.tar.gz -o keystone-${VERSION}.tar.gz \
    && tar xvf keystone-${VERSION}.tar.gz \
    && cd keystone-${VERSION} \
    && pip install pika==0.10.0 \
    && pip install -r requirements.txt \
    && PBR_VERSION=${VERSION}  pip install . \
    && pip install uwsgi MySQL-python \
    && cp -r etc /etc/keystone \
    && cd - \
    && rm -rf keystone-${VERSION}*

RUN apt install python-openstackclient -y
COPY keystone.conf /etc/keystone/keystone.conf
COPY keystone.sql /root/keystone.sql
COPY multi_policy.json /etc/keystone/

COPY tm_dump.sql /root/topology.sql

# Add bootstrap script and make it executable
COPY bootstrap.sh /etc/bootstrap.sh
RUN chown root:root /etc/bootstrap.sh && chmod a+x /etc/bootstrap.sh

CMD ["/etc/bootstrap.sh"]
EXPOSE 5000 35357
