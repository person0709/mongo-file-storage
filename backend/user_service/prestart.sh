#! /usr/bin/env bash

# This script will run first when a container is created

# Let the DB start
sleep 15;
# Run migrations
alembic upgrade head

# Add superuser if not present
python app/init_db.py