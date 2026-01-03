<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 1.5.7

- Fix add-on startup failure by updating base image from Alpine 3.15 to Alpine 3.21
- Align Alpine version with Invidious upstream image for compatibility
- Base image now uses ghcr.io/home-assistant/amd64-base:3.21

## 1.5.6

- Add startup confirmation log message when Invidious successfully starts and is listening on port 3000
- Background health check confirms service is actually responding before declaring success

## 1.5.5

- Update devcontainer name from generic template to "Invidious Add-on devcontainer"

## 1.5.4

- Fix supervisor watchdog restart loop by keeping container alive on service failure
- Add TCP healthcheck watchdog configuration for proper service health monitoring
- Prevent container exit when Invidious service fails, eliminating rapid restart cycles
- Replace exit code 125 approach with indefinite sleep to maintain container state

## 1.5.3

- Fix s6-overlay error "can only run as pid 1" by removing conflicting init: true setting
- Fix shellcheck lint errors by adding shell directive to service scripts
- Improve compatibility with Home Assistant base image s6-overlay init system

## 1.5.2

- Fix supervisor rate limiting issue caused by rapid restart loops
- Add proper service halt on failures to prevent continuous restarts
- Improve finish script to exit with code 125 on errors, signaling s6-overlay to stop
- Enhance error logging to indicate when service is being halted

## 1.5.1

- Fix critical restart loop issue causing supervisor rate limiting
- Remove automatic container halt on Invidious exit to prevent restart loops
- Add additional logging and binary verification checks
- Improve error messages for debugging startup issues

## 1.5.0

- Version bump for new release

## 1.4.0

- Update Invidious to latest version
- Fix critical architecture mismatch in CI/CD pipeline (remove aarch64)
- Fix repository URL typo in README.md
- Improve shell script error handling and quoting

## 1.3.3

- Fix s6-applyuidgid permission errors by enabling init system

## 1.3.2

- Update Invidious version

## 1.3.1

- Fix su-exec permission errors by replacing with s6-setuidgid
- Remove ARM64 (aarch64) support due to upstream Invidious image limitations
- Refactor Dockerfile to use multi-stage build pattern
- Fix repository URLs across all configuration files

## 1.3.0

- Implement actual Invidious functionality
- Remove template "Hello World" message
- Add PostgreSQL database integration
- Configure Invidious web interface on port 3000
- Rename directory from 'example' to 'invidious'
- Fix "Service restart after closing" log message
- Enable web interface access

## 1.2.0

- Add an apparmor profile
- Update to 3.15 base image with s6 v3
- Add a sample script to run as service and constrain in aa profile

## 1.1.0

- Updates

## 1.0.0

- Initial release
