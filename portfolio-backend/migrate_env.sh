#!/bin/bash
# Migration script for .env file to new rate limiting configuration

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found!"
    echo "Please create one from .env.example"
    exit 1
fi

echo "Migrating .env file to new rate limiting configuration..."
echo "Creating backup: .env.backup"
cp "$ENV_FILE" "$ENV_FILE.backup"

# Remove old rate limiting variables
sed -i.tmp '/^RATE_LIMIT_NATURAL_MODE=/d' "$ENV_FILE"
sed -i.tmp '/^RATE_LIMIT_LISTEN_MODE=/d' "$ENV_FILE"
sed -i.tmp '/^RATE_LIMIT_PER_HOUR=/d' "$ENV_FILE"
rm -f "$ENV_FILE.tmp"

# Add new rate limiting configuration if not already present
if ! grep -q "RATE_LIMIT_NATURAL_DAILY" "$ENV_FILE"; then
    echo "" >> "$ENV_FILE"
    echo "# Rate Limiting (centralized configuration)" >> "$ENV_FILE"
    echo "# Natural Mode (LLM-powered chatbot)" >> "$ENV_FILE"
    echo "RATE_LIMIT_NATURAL_DAILY=20      # Max requests per day per IP" >> "$ENV_FILE"
    echo "RATE_LIMIT_NATURAL_MONTHLY=100   # Max requests per month per IP" >> "$ENV_FILE"
    echo "" >> "$ENV_FILE"
    echo "# Listen Mode (search-only, no LLM)" >> "$ENV_FILE"
    echo "RATE_LIMIT_LISTEN_DAILY=40       # Max requests per day per IP" >> "$ENV_FILE"
    echo "RATE_LIMIT_LISTEN_MONTHLY=200    # Max requests per month per IP" >> "$ENV_FILE"
fi

echo "✅ Migration completed successfully!"
echo "Backup saved to: .env.backup"
echo ""
echo "New rate limits:"
echo "  Natural Mode: 20/day, 100/month per IP"
echo "  Listen Mode: 40/day, 200/month per IP"
