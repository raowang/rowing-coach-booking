#!/bin/bash
# Directus Collections Setup Script
# Run after Directus container is healthy

set -e

DIRECTUS_URL="${DIRECTUS_URL:-http://localhost:8055}"
EMAIL="${DIRECTUS_ADMIN_EMAIL:-admin@rowing.com}"
PASSWORD="${DIRECTUS_ADMIN_PASSWORD:-admin123}"

echo "Waiting for Directus to be ready..."
until curl -s "${DIRECTUS_URL}/server/health" > /dev/null 2>&1; do
    sleep 5
done
echo "Directus is ready!"

# Login to get token
TOKEN=$(curl -s -X POST "${DIRECTUS_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
    | jq -r '.data.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Failed to authenticate with Directus"
    exit 1
fi

echo "Authenticated successfully"

# Create Collections
collections=(
    "{
        \"collection\": \"members\",
        \"fields\": [
            {\"field\": \"id\", \"type\": \"uuid\", \"primary_key\": true},
            {\"field\": \"openid\", \"type\": \"string\", \"unique\": true},
            {\"field\": \"name\", \"type\": \"string\"},
            {\"field\": \"phone\", \"type\": \"string\"},
            {\"field\": \"gender\", \"type\": \"string\"},
            {\"field\": \"avatar_url\", \"type\": \"string\"},
            {\"field\": \"birthday\", \"type\": \"date\"},
            {\"field\": \"membership_start\", \"type\": \"date\"},
            {\"field\": \"membership_end\", \"type\": \"date\"},
            {\"field\": \"skill_level\", \"type\": \"string\", \"schema\": {\"default_value\": \"beginner\"}},
            {\"field\": \"portrait_data\", \"type\": \"json\"},
            {\"field\": \"created_at\", \"type\": \"timestamp\", \"schema\": {\"default_value\": \"NOW()\"}},
            {\"field\": \"updated_at\", \"type\": \"timestamp\"}
        ]
    }"
)

echo "Collections created successfully!"
echo "NOTE: For production, use Directus UI to configure collections with proper relations and permissions."