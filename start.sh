#!/usr/bin/env bash
exec odoo --addons-path=addons,$PWD/odoo/addons \
          --db_user=$DB_USER \
          --db_password=$DB_PASSWORD \
          --db_host=$DB_HOST \
          --db_port=$DB_PORT \
          --http-port=$PORT \
          --without-demo=all \
          -i base
