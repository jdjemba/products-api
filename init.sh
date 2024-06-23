#!/bin/sh
set -e

echo "Start executing the init.sh script .... "

export FLASK_APP=app.py

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "Initialize database migrations"
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
else
    echo "Migrations directory already exists. Skipping initialization."
    flask db upgrade
fi

python insert_data.py
echo "Finished initializing the database"

exec python app.py
