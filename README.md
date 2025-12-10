# Dag Hello World

Hello World Dagster module for testing

## Quick Start

### Local Development

1. **Integrate with workspace** (if not already done):
   ```bash
   @dagster-module-builder workspace add dag-hello-world
   ```

2. **Start workspace Dagster**:
   ```bash
   cd ~/workspace/services/dagster
   docker-compose up -d
   ```

3. **Open Dagster UI**:
   ```
   http://localhost:3000
   ```

4. **Materialize assets**:
   - Navigate to Assets
   - Find `dag_hello_world/*` assets
   - Click Materialize

### Standalone Testing (Optional)

```bash
cd ~/workspace/projects/dag-hello-world
docker-compose up -d  # If database needed
dagster dev -f src/dag_hello_world_dagster/__init__.py
```

## Project Structure

```
dag-hello-world/
├── src/
│   └── dag_hello_world_dagster/
│       ├── __init__.py          # Dagster definitions
│       ├── assets.py            # Asset definitions
│       └── resources.py         # Custom IO manager
├── workspace/                   # Workspace integration
│   └── local/
├── deploy/                      # Deployment configs
├── pyproject.toml
├── requirements.txt
└── README.md                    # This file
```

## Assets

### `sample_asset`
- **Description**: Sample asset demonstrating basic patterns
- **Compute Kind**: python
- **Outputs**: Dict with status and metadata

## Configuration

### Environment Variables

See `.env.example` for all required variables:
- Database connection (if applicable)
- Module-specific settings

### Workspace Integration

This module integrates with `~/workspace/services/dagster/`:
- Workspace entry in `workspace.yaml`
- Environment variables in `.env`
- Database service in `docker-compose.yml`

## Deployment

See `deploy/production/DEPLOYMENT.md` for deployment instructions specific to each environment.

## Development

### Adding New Assets

1. Define asset in `src/dag_hello_world_dagster/assets.py`
2. Import in `__init__.py`
3. Add to Definitions
4. Test locally

### Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=src/dag_hello_world_dagster --cov-report=html
```

## Troubleshooting

### Asset not appearing in UI
- Check workspace.yaml has correct entry
- Restart Dagster: `docker-compose restart dagster_webserver`

### Database connection fails
- Verify database container is running: `docker ps`
- Check environment variables in .env

### Storage errors
- Custom IO manager uses `/tmp/dagster_storage/`
- Verify volume mount in docker-compose.yml

## Documentation

- **SETUP.md** - Detailed setup instructions
- **TROUBLESHOOTING.md** - Common issues and solutions
- **deploy/production/DEPLOYMENT.md** - Deployment guide

---

**Status**: Development
**Created**: 2025-12-10
**Last Updated**: 2025-12-10
