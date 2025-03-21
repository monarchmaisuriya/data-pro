#!/bin/bash

# Function to display error messages and exit
error_exit() {
    echo "$1" >&2
    exit 1
}

# Function to validate environment
validate_environment() {
    local env=$1
    if [[ "$env" != "development" && "$env" != "production" ]]; then
        error_exit "Error: Invalid environment. Use 'development' or 'production'."
    fi
}

# Function to validate action
validate_action() {
    local action=$1
    if [[ "$action" != "start" && "$action" != "stop" && "$action" != "restart" && "$action" != "remove" ]]; then
        error_exit "Error: Invalid action. Use 'start', 'stop', 'restart', or 'remove'."
    fi
}

# Determine the correct Docker Compose command (prefer "docker compose" over "docker-compose")
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    error_exit "Error: Docker Compose not found. Please install Docker and Docker Compose."
fi

# Parse command line arguments
ACTION=""
ENVIRONMENT="development" # Default environment

while [[ $# -gt 0 ]]; do
    case $1 in
        --action=*)
            ACTION="${1#*=}"
            ;;
        --environment=*)
            ENVIRONMENT="${1#*=}"
            ;;
        *)
            error_exit "Error: Unknown argument '$1'"
            ;;
    esac
    shift
done

# Validate inputs
if [[ -z "$ACTION" ]]; then
    error_exit "Error: Action is required. Use --action={start/stop/restart/remove}"
fi

validate_action "$ACTION"
validate_environment "$ENVIRONMENT"

# Set environment variables
if [[ "$ENVIRONMENT" == "production" ]]; then
    export TARGET=production
else
    export TARGET=development
fi

# Execute the requested action
case "$ACTION" in
    start)
        echo "Starting services in $ENVIRONMENT environment..."
        $DOCKER_COMPOSE_CMD up -d
        ;;
    stop)
        echo "Stopping services in $ENVIRONMENT environment..."
        $DOCKER_COMPOSE_CMD down
        ;;
    restart)
        echo "Restarting services in $ENVIRONMENT environment..."
        $DOCKER_COMPOSE_CMD down
        $DOCKER_COMPOSE_CMD up -d
        ;;
    remove)
        echo "Removing services and cleaning up in $ENVIRONMENT environment..."
        $DOCKER_COMPOSE_CMD down -v --rmi all --remove-orphans
        ;;

esac