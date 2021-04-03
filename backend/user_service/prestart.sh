#! /usr/bin/env bash

# This script will run first when a container is created

# Let the DB start
sleep 20;
# Run migrations
alembic upgrade head