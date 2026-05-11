# Local App Health Report

## Env Validation: PASS

## Service Health
- **local-db**: container_running=False, container_health=unknown, api_usable=False (no API check configured)
- **local-queue**: container_running=False, container_health=unknown, api_usable=False (no API check configured)
- **local-app**: container_running=False, container_health=unknown, api_usable=False (unreachable: <urlopen error [Errno 111] Connection refused>)
- **local-worker**: container_running=False, container_health=unknown, api_usable=False (no API check configured)
- **local-api**: container_running=False, container_health=unknown, api_usable=False (unreachable: <urlopen error [Errno 111] Connection refused>)

## Startup Dependency Order: FAIL
- ⚠️ local-app depends on local-db, but local-db is not running
- ⚠️ local-app depends on local-queue, but local-queue is not running
- ⚠️ local-worker depends on local-db, but local-db is not running
- ⚠️ local-worker depends on local-queue, but local-queue is not running
- ⚠️ local-api depends on local-app, but local-app is not running

## Port Conflicts: PASS

## Volume Existence: FAIL
- ⚠️ {'service': 'local-db', 'path': '/workspace/sdlc-skill-pack/local_apps/data/postgres'}
- ⚠️ {'service': 'local-db', 'path': '/workspace/sdlc-skill-pack/local_apps/backups'}
- ⚠️ {'service': 'local-queue', 'path': '/workspace/sdlc-skill-pack/local_apps/data/redis'}
- ⚠️ {'service': 'local-api', 'path': '/workspace/sdlc-skill-pack/local_apps/nginx/default.conf'}

## Backup Readiness: PASS
- ok

## Upgrade/Migration Warnings
- none
