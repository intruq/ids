# Deployment

`Docker`-based distributed deployment of IDS components

# Installation instructions

```
docker-compose build
docker-compose up
```

### Port Mapping:
The docker-compose file exposes three ports for public use:

- Port 9000 - Visualization MOSAIK
- Port 8999 - Visualization IDS
- Port 8777 - Websocket for Requirement Violations

### Directory Structure
- **config**: config files
- **testbed**: MOSAIK Testbed