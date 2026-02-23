#!/bin/bash
# View ExcelFlow Docker logs

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📋 Viewing all service logs (Ctrl+C to exit)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if docker compose version &> /dev/null; then
        docker compose logs -f
    else
        docker-compose logs -f
    fi
else
    echo "📋 Viewing $SERVICE logs (Ctrl+C to exit)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if docker compose version &> /dev/null; then
        docker compose logs -f "$SERVICE"
    else
        docker-compose logs -f "$SERVICE"
    fi
fi
