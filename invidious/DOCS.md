# Home Assistant Add-on: Invidious

## How to use

This add-on provides Invidious, a privacy-friendly alternative YouTube frontend.

When started, it will:
- Initialize a PostgreSQL database for Invidious (stored in `/data/postgresql`)
- Generate a secure HMAC key for the instance
- Start the Invidious web interface on port 3000

Access the Invidious web interface through Home Assistant's Ingress panel or directly at:
`http://[your-home-assistant-ip]:3000`

## Configuration

This add-on currently requires no additional configuration. All necessary settings are automatically configured during startup.

The add-on will:
- Automatically create and manage the PostgreSQL database
- Generate a unique HMAC key for security
- Configure Invidious to listen on port 3000

## Data Persistence

The following data is persisted in the `/data` directory:
- PostgreSQL database files
- HMAC key for the instance

This ensures your Invidious instance maintains its state across restarts.
