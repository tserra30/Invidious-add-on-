# Copilot Instructions for Invidious Add-on

## Repository Overview

This repository contains a Home Assistant add-on for Invidious, a privacy-friendly YouTube frontend. The add-on packages Invidious with PostgreSQL in a Docker container that integrates with Home Assistant's supervisor system.

## Project Structure

- `invidious/` - Main add-on directory
  - `config.yaml` - Add-on configuration (version, ports, architecture)
  - `build.yaml` - Docker build configuration
  - `Dockerfile` - Multi-stage build using official Invidious image
  - `rootfs/` - Files copied into the container at root
    - `etc/services.d/invidious/` - s6-overlay service scripts
  - `DOCS.md` - User-facing documentation
  - `CHANGELOG.md` - Version history
- `.github/workflows/` - CI/CD pipelines
  - `builder.yaml` - Builds and publishes Docker images to GHCR
  - `lint.yaml` - Runs Home Assistant add-on linter

## Development Guidelines

### Home Assistant Add-on Conventions

1. **Configuration Files**:
   - Follow Home Assistant add-on configuration schema: https://developers.home-assistant.io/docs/add-ons/configuration
   - `config.yaml` defines add-on metadata, ports, options, and schema
   - Version must follow semantic versioning (e.g., "1.5.2")
   - Update `CHANGELOG.md` when incrementing version

2. **Docker Image**:
   - Base image: `ghcr.io/home-assistant/amd64-base:3.15` (uses s6-overlay v3)
   - Images published to: `ghcr.io/tserra30/{arch}-addon-invidious`
   - Multi-stage build pulls Invidious from official image: `quay.io/invidious/invidious:latest`

3. **Service Management**:
   - Use s6-overlay service scripts in `rootfs/etc/services.d/`
   - Scripts must be executable and use `#!/usr/bin/with-contenv bashio` shebang
   - `run` - Starts the service
   - `finish` - Cleanup when service stops
   - Use `bashio::log.*` functions for logging
   - Use `s6-setuidgid` for running commands as specific users

4. **Data Persistence**:
   - Data persisted in `/data/` directory (mapped by Home Assistant)
   - PostgreSQL database stored in `/data/postgresql`
   - HMAC key stored in `/data/hmac_key`

### Bash Scripts

- Use `bashio::log.info`, `bashio::log.error` for logging
- Include error handling with `|| { bashio::log.error "message"; exit 1; }`
- Use `s6-setuidgid` instead of `su` or `sudo` for user switching
- Include ShellCheck directive: `# shellcheck shell=bash`

### Build and Test

1. **Linting**: 
   - GitHub Action runs `frenck/action-addon-linter` on all add-ons
   - Validates add-on configuration files

2. **Building**:
   - Comment out `image:` key in `config.yaml` during development to build locally
   - Restore `image:` key before pushing to trigger CI build
   - CI builds and tests on push/PR to main branch
   - Production builds push to GHCR on merge to main

3. **Testing**:
   - Builder workflow uses `--test` flag for PR builds
   - Test builds do not push to registry

### Workflow

1. Development changes should NOT modify the `image:` property in production
2. Increment version in `config.yaml` when merging to main
3. Update `CHANGELOG.md` with version changes
4. CI automatically builds and publishes on merge to main
5. First-time setup may require:
   - Making GHCR packages public
   - Setting GitHub Actions permissions to "Read & Write"

## Security Considerations

- PostgreSQL runs with hardcoded credentials (`invidious:invidious`) - this is acceptable because:
  - The database is configured to listen only on localhost within the container
  - The container network is isolated with no external access to PostgreSQL
  - This is a standard practice for containerized single-service databases
- HMAC key is randomly generated on first run and persisted in `/data/hmac_key` for security
- The container environment provides network isolation - only the Invidious service on port 3000 is exposed

## Common Tasks

### Adding Configuration Options

1. Add option to `options:` and define in `schema:` in `config.yaml`
2. Access options in scripts using `bashio::config` functions
3. Update `DOCS.md` to document new options

### Updating Invidious Version

1. Dockerfile pulls `quay.io/invidious/invidious:latest`
2. To pin a specific version, change the tag in the Dockerfile
3. Test the build locally first

### Modifying Service Startup

1. Edit `rootfs/etc/services.d/invidious/run`
2. Ensure proper error handling and logging
3. Use `exec` on the final command to replace the shell process

## References

- Home Assistant Add-on Documentation: https://developers.home-assistant.io/docs/add-ons
- s6-overlay Documentation: https://github.com/just-containers/s6-overlay
- Bashio Documentation: https://github.com/hassio-addons/bashio
- Invidious Project: https://github.com/iv-org/invidious
