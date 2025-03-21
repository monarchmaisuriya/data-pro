# Data Pro - Distributed Task Scheduling Service

A modern task scheduling service that allows users to schedule and manage tasks with various intervals or on-demand execution. The service efficiently manages tasks, scales automatically, and handles failures gracefully.

## Features

- Task scheduling with flexible intervals and on-demand execution
- Support for different task types (scripts, API calls, background jobs)
- Dynamic worker scaling based on demand
- Task dependencies and automatic retries
- Comprehensive logging and monitoring
- User-friendly web interface and REST API

## Tech Stack

### Frontend (Client)

- React with TypeScript and Vite
- Shadcn UI for UI components

### Backend (Server)

- FastAPI (Python)
- PostgreSQL database

## Prerequisites

- [Docker](https://www.docker.com/)
- [uv](https://docs.astral.sh/uv/) for Python package management

## Project Structure

```
├── client/          # React frontend application
├── server/          # FastAPI backend application
├── docker-compose.yml         # Production Docker configuration
├── docker-compose.override.yml # Development Docker configuration
└── orchestrate.sh   # Project management script
```

## Development Setup

1. Clone the repository

2. Make the orchestrate script executable:

   ```bash
   chmod +x orchestrate.sh
   ```

3. Use the orchestrate script to manage the application:

   ```bash
   # Start in development mode (with hot-reload)
   ./orchestrate.sh --action=start --environment=development

   # Start in production mode
   ./orchestrate.sh --action=start --environment=production

   # Stop the services
   ./orchestrate.sh --action=stop

   # Restart services
   ./orchestrate.sh --action=restart

   # Remove all containers, volumes, and images
   ./orchestrate.sh --action=remove
   ```

   This will start:

   - Frontend at http://localhost:5173
   - Backend at http://localhost:8000
   - PostgreSQL at localhost:5432

## Using the Orchestrate Script

The `orchestrate.sh` script provides a convenient way to manage the application's Docker services:

### Available Actions

- `start`: Launch the services
- `stop`: Stop all running services
- `restart`: Restart all services
- `remove`: Remove all containers, volumes, and images

### Environments

- `development`: Runs with hot-reload enabled (default)
- `production`: Runs in production mode

## Services

### Client (Frontend)

- Development server runs on port 5173
- Built with React + TypeScript + Vite
- Features hot module replacement (HMR)
- Configured with ESLint for code quality

### Server (Backend)

- FastAPI server runs on port 8000
- PostgreSQL database on port 5432
- Uses uv for Python package management

### Database

- PostgreSQL 15 with Alpine-based image
- Persistent data storage using Docker volumes
- Includes health checks for reliability
