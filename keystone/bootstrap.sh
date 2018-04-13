#!/bin/bash

export OS_AUTH_URL=http://localhost:35357/v3
export OS_IDENTITY_API_VERSION=3
export OS_PROJECT_DOMAIN_ID=default
export OS_PROJECT_NAME=admin
export OS_PASSWORD=${ADMIN_PASSWORD}
export OS_USERNAME=admin

CONFIG_FILE=/etc/keystone/keystone.conf
SQL_SCRIPT=/root/keystone.sql
TOPOLOGY_DUMP=/root/topology.sql

sleep 10
echo "Waiting for mysql"
until mysql -h 127.0.0.1 -u root -proot &> /dev/null
do
  printf "."
  sleep 10
done
echo -e "\nmysql ready"
mysql -u root -proot -h 127.0.0.1 <$SQL_SCRIPT
rm -f $SQL_SCRIPT

# Populate the Identity service database
mkdir /var/log/keystone/

echo "keystone-Manage Operations"
keystone-manage db_sync
keystone-manage fernet_setup --keystone-user root --keystone-group root
keystone-manage credential_setup --keystone-user root --keystone-group root

mv /etc/keystone/default_catalog.templates /etc/keystone/default_catalog

# start keystone service
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin) &

sleep 5 # wait for start

echo "keystone-Manage Bootstrap"
keystone-manage bootstrap --bootstrap-password $OS_PASSWORD \
  --bootstrap-admin-url http://localhost:35357/v3/ \
  --bootstrap-internal-url http://localhost:35357/v3/ \
  --bootstrap-public-url http://localhost:5000/v3/ \
  --bootstrap-region-id RegionOne
sleep 5
echo "Add role"
openstack role add --domain default --user admin admin
sleep 5
openstack role create user
sleep 5
mv /etc/keystone/multi_policy.json /etc/keystone/policy.json

# reboot services
pkill uwsgi
sleep 5
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-public) &
sleep 5
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin)
