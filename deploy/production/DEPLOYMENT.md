# Deployment Guide: dag_hello_world → production (Git Strategy)

**Client:** Test Client
**Environment:** production
**Strategy:** Git repository checkout
**Last Updated:** 2025-12-10

---

## Prerequisites

- [ ] Git repository: git@github.com:myorg/dag-hello-world.git
- [ ] SSH access to <REMOTE_HOST> as <REMOTE_USER>
- [ ] Module code committed to `main` branch
- [ ] Remote server has git installed

---

## Initial Setup (First Deploy Only)

### Step 1: Clone Repository on Remote Server

```bash
# SSH into production server
ssh <REMOTE_USER>@<REMOTE_HOST>

# Navigate to modules directory
cd /opt/dagster/modules

# Clone repository
git clone git@github.com:myorg/dag-hello-world.git dag_hello_world

# Verify
cd dag_hello_world
git branch
git log -1 --oneline
```

### Step 2: Update Remote Configuration Files

#### 2.1 Update `.env`
```bash
ssh <REMOTE_USER>@<REMOTE_HOST>

# Add these variables to /opt/dagster/.env
cat >> /opt/dagster/.env << 'EOF'

# Dag Hello World Configuration
DAG_HELLO_WORLD_DB_HOST=dag_hello_world_postgres
DAG_HELLO_WORLD_DB_PORT=5440
DAG_HELLO_WORLD_DB_USER=dag_hello_world_user
DAG_HELLO_WORLD_DB_PASSWORD=<CHANGE_THIS_IN_PRODUCTION>
DAG_HELLO_WORLD_DB_NAME=dag_hello_world_db
EOF
```

#### 2.2 Update `workspace.yaml`
```bash
# Add module entry
cat >> /opt/dagster/workspace.yaml << 'EOF'

# BEGIN: dag_hello_world
- python_package:
    package_name: dag_hello_world_dagster
    working_directory: /workspace/modules/dag_hello_world/src
# END: dag_hello_world
EOF
```

#### 2.3 Update `docker-compose.yml`
Add database service for this module:

```yaml
services:
  # ... existing services ...

  # Dag Hello World Database
  dag_hello_world_postgres:
    image: postgres:${POSTGRES_VERSION:-15}
    container_name: dag_hello_world_postgres
    environment:
      POSTGRES_USER: ${DAG_HELLO_WORLD_DB_USER}
      POSTGRES_PASSWORD: ${DAG_HELLO_WORLD_DB_PASSWORD}
      POSTGRES_DB: ${DAG_HELLO_WORLD_DB_NAME}
    volumes:
      - ${DATA_PATH}/postgres/dag_hello_world:/var/lib/postgresql/data
    ports:
      - "${DAG_HELLO_WORLD_DB_PORT}:5432"
    networks:
      - ${NETWORK_NAME}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${DAG_HELLO_WORLD_DB_USER}"]
      interval: 30s
      timeout: 5s
      retries: 3

  # Update dependencies
  dagster_webserver:
    depends_on:
      # ... existing dependencies ...
      dag_hello_world_postgres:
        condition: service_healthy

  dagster_daemon:
    depends_on:
      # ... existing dependencies ...
      dag_hello_world_postgres:
        condition: service_healthy
```

#### 2.4 Update `Dockerfile`
Add module dependencies:

```dockerfile
# Dag Hello World dependencies
RUN pip install --no-cache-dir \
    # Add module-specific packages

ENV PYTHONPATH="${PYTHONPATH}:/workspace/modules/dag_hello_world/src"
```

### Step 3: Build and Start Services

```bash
ssh <REMOTE_USER>@<REMOTE_HOST>

cd /opt/dagster
docker-compose build
docker-compose up -d
```

### Step 4: Verify Initial Deployment

```bash
# Check logs
ssh <REMOTE_USER>@<REMOTE_HOST> 'docker logs workspace_dagster_webserver --tail 50'

# Check Dagster UI
# Open http://<REMOTE_HOST>:3000
# Navigate to Assets → Should see dag_hello_world/* assets
```

---

## Regular Deployment (After Initial Setup)

### Step 1: Push Code to Repository

```bash
# On your local machine
cd ~/workspace/projects/dag-hello-world

# Ensure you're on main branch
git checkout main

# Commit your changes
git add src/
git commit -m "feat: update dag_hello_world"

# Push to remote
git push origin main
```

### Step 2: Deploy to Production

**Option A: Manual Pull**
```bash
# SSH into production
ssh <REMOTE_USER>@<REMOTE_HOST>

# Pull latest changes
cd /opt/dagster/modules/dag_hello_world
git pull origin main

# Rebuild and restart
cd /opt/dagster
docker-compose build
docker-compose up -d --no-deps dagster_webserver dagster_daemon
```

**Option B: One-Command Deploy** (Recommended)
```bash
# From your local machine
ssh <REMOTE_USER>@<REMOTE_HOST> '\
  cd /opt/dagster/modules/dag_hello_world && \
  git pull origin main && \
  cd /opt/dagster && \
  docker-compose build && \
  docker-compose up -d --no-deps dagster_webserver dagster_daemon'
```

### Step 3: Verify Deployment

```bash
# Check git status on remote
ssh <REMOTE_USER>@<REMOTE_HOST> '\
  cd /opt/dagster/modules/dag_hello_world && \
  git log -1 --oneline'

# Check Dagster logs
ssh <REMOTE_USER>@<REMOTE_HOST> '\
  docker logs workspace_dagster_webserver --tail 50 | grep dag_hello_world'

# Test in Dagster UI
# http://<REMOTE_HOST>:3000
```

---

## Rollback Procedure

### Quick Rollback to Previous Commit

```bash
# SSH into production
ssh <REMOTE_USER>@<REMOTE_HOST>

# Navigate to module
cd /opt/dagster/modules/dag_hello_world

# View recent commits
git log --oneline -5

# Rollback to previous commit
git reset --hard HEAD~1

# Or rollback to specific commit
git reset --hard <commit-hash>

# Restart services
cd /opt/dagster
docker-compose up -d --no-deps dagster_webserver dagster_daemon
```

### Verify Rollback

```bash
# Check current commit
ssh <REMOTE_USER>@<REMOTE_HOST> '\
  cd /opt/dagster/modules/dag_hello_world && \
  git log -1 --oneline'
```

---

## Troubleshooting

### Issue: Git pull fails with conflicts

**Solution:**
```bash
ssh <REMOTE_USER>@<REMOTE_HOST>
cd /opt/dagster/modules/dag_hello_world

# Stash local changes (if any)
git stash

# Pull latest
git pull origin main

# If conflicts persist, hard reset
git fetch origin
git reset --hard origin/main
```

### Issue: Module not appearing in Dagster UI

**Checklist:**
- [ ] Module entry in workspace.yaml?
- [ ] PYTHONPATH includes module path in Dockerfile?
- [ ] Dagster containers restarted after changes?
- [ ] No errors in webserver logs?

**Debug:**
```bash
# Check workspace.yaml
ssh <REMOTE_USER>@<REMOTE_HOST> 'grep -A 3 "dag_hello_world" /opt/dagster/workspace.yaml'

# Check logs for errors
ssh <REMOTE_USER>@<REMOTE_HOST> 'docker logs workspace_dagster_webserver 2>&1 | grep -i error'
```

### Issue: Database connection fails

**Solution:**
```bash
# Check database container
ssh <REMOTE_USER>@<REMOTE_HOST> 'docker ps | grep dag_hello_world_postgres'

# Check database logs
ssh <REMOTE_USER>@<REMOTE_HOST> 'docker logs dag_hello_world_postgres --tail 50'

# Test connection
ssh <REMOTE_USER>@<REMOTE_HOST> '\
  docker exec dag_hello_world_postgres psql \
    -U dag_hello_world_user \
    -d dag_hello_world_db \
    -c "SELECT 1"'
```

---

## Deployment Checklist

**Initial Setup:**
- [ ] Repository cloned on remote server
- [ ] `.env` updated with module variables
- [ ] `workspace.yaml` updated with module entry
- [ ] `docker-compose.yml` updated with database service
- [ ] `Dockerfile` updated with dependencies
- [ ] Services built and started
- [ ] Module visible in Dagster UI
- [ ] Test asset materialization successful

**Regular Deployment:**
- [ ] Code committed and pushed to main
- [ ] Remote pulled latest changes
- [ ] Services rebuilt and restarted
- [ ] Deployment verified in UI
- [ ] No errors in logs

---

## Quick Reference Commands

```bash
# Deploy latest
ssh <REMOTE_USER>@<REMOTE_HOST> 'cd /opt/dagster/modules/dag_hello_world && git pull && cd /opt/dagster && docker-compose up -d --no-deps dagster_webserver dagster_daemon'

# Check status
ssh <REMOTE_USER>@<REMOTE_HOST> 'cd /opt/dagster/modules/dag_hello_world && git log -1 --oneline'

# View logs
ssh <REMOTE_USER>@<REMOTE_HOST> 'docker logs workspace_dagster_webserver --tail 100 | grep dag_hello_world'

# Rollback
ssh <REMOTE_USER>@<REMOTE_HOST> 'cd /opt/dagster/modules/dag_hello_world && git reset --hard HEAD~1 && cd /opt/dagster && docker-compose up -d --no-deps dagster_webserver dagster_daemon'
```

---

**For questions or issues, refer to:**
- Module README: `/opt/dagster/modules/dag_hello_world/README.md`
- Dagster docs: https://docs.dagster.io/
- Project documentation: ~/workspace/projects/dag-hello-world/docs/
