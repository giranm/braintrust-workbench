#!/bin/bash
set -e

echo "🚀 Starting Frappe Helpdesk initialization..."

BENCH_DIR="/home/frappe/frappe-bench"
SITE_NAME="support-desk.localhost"

# Check if bench already initialized
if [ -d "$BENCH_DIR/apps" ]; then
    echo "✅ Bench already exists, starting services..."
    cd "$BENCH_DIR"
    bench start
else
    echo "📦 Creating new bench..."
    cd /home/frappe
    bench init --skip-redis-config-generation frappe-bench --version version-16

    cd "$BENCH_DIR"

    echo "⚙️  Configuring services..."
    # Use container hostnames instead of localhost
    bench set-mariadb-host mariadb
    bench set-redis-cache-host redis://redis:6379
    bench set-redis-queue-host redis://redis:6379
    bench set-redis-socketio-host redis://redis:6379

    # Remove redis and watch from Procfile (we're using external containers)
    sed -i '/redis/d' ./Procfile
    sed -i '/watch/d' ./Procfile

    echo "📥 Installing apps..."
    bench get-app telephony
    bench get-app helpdesk

    echo "🏗️  Creating site..."
    bench new-site "$SITE_NAME" \
        --force \
        --mariadb-root-password 123 \
        --admin-password admin123 \
        --no-mariadb-socket

    echo "📲 Installing apps on site..."
    bench --site "$SITE_NAME" install-app telephony
    bench --site "$SITE_NAME" install-app helpdesk

    echo "⚙️  Configuring site..."
    bench --site "$SITE_NAME" set-config developer_mode 1
    bench --site "$SITE_NAME" set-config mute_emails 1
    bench --site "$SITE_NAME" set-config server_script_enabled 1
    bench --site "$SITE_NAME" clear-cache

    bench use "$SITE_NAME"

    echo "🌱 Seeding database with initial configuration..."
    # Apply seed data (webhooks, demo data, etc.)
    if [ -f "/workspace/seed-db.sql" ]; then
        # Get the database name from site config
        DB_NAME=$(cat "$BENCH_DIR/sites/$SITE_NAME/site_config.json" | grep -o '"db_name": *"[^"]*"' | grep -o '"[^"]*"$' | tr -d '"')

        if [ -n "$DB_NAME" ]; then
            echo "📊 Applying seed data to database: $DB_NAME"
            mariadb -h mariadb -u root -p123 "$DB_NAME" < /workspace/seed-db.sql
            echo "✅ Seed data applied successfully"
        else
            echo "⚠️  Could not determine database name, skipping seed data"
        fi
    else
        echo "⚠️  Seed script not found at /workspace/seed-db.sql"
    fi

    echo "✅ Initialization complete!"
    bench start
fi
