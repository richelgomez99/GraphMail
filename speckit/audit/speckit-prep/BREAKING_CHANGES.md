# BREAKING CHANGES - Migration Guide

**Purpose**: Document all changes that will break existing functionality  
**Audience**: Developers maintaining GRAPHMAIL  
**Status**: PLANNED (not yet implemented)

---

## Overview

The transition from **hackathon prototype → production system** will introduce breaking changes to:
- File structure
- API interfaces
- Data formats
- Configuration
- Dependencies

**Mitigation**: This document provides migration paths for each breaking change.

---

## PHASE 1: File Structure Changes

### Breaking Change 1.1: Demo File Deletion

**What's Changing**:
```bash
# These files will be DELETED:
demo_clear.py
demo_collaboration_graph.py
demo_final.py
demo_final_complete.py
demo_simple.py
demo_track9.py
demo_human.py (consolidated)
demo_complete_graph.py (consolidated)
```

**Impact**: Scripts/docs referencing these files will break

**Migration**:
```bash
# Before
python demo_simple.py

# After
python demo_dashboard.py --mode=simple
```

**Affected**:
- `run_demo.sh` (needs update)
- `README.md` (needs update)
- Any CI/CD scripts

**Timeline**: Week 1, Day 1

---

### Breaking Change 1.2: Source Code Reorganization

**What's Changing**:
```
# Old structure
src/
  agents/
    agent1_parser.py
    agent2_extractor.py
    agent3_verifier.py

# New structure
src/
  agents/
    parser.py
    extractor.py
    verifier.py
  utils/
    llm.py          # NEW - extracted
    retry.py        # NEW - extracted
    cache.py        # NEW - extracted
  config/
    settings.py     # NEW - centralized config
```

**Impact**: Import statements will break

**Migration**:
```python
# Before
from src.agents.agent1_parser import agent_1_parser
from src.agents.agent2_extractor import agent_2_extractor

# After
from src.agents.parser import parse_emails
from src.agents.extractor import extract_intelligence
```

**Affected**: All files importing agents

**Timeline**: Week 1, Day 2

---

## PHASE 2: Configuration Changes

### Breaking Change 2.1: Configuration File Required

**What's Changing**:
- Hardcoded values → centralized config
- `.env` variables → `settings.py`

**Impact**: Running without `.env` will fail

**Migration**:
```bash
# Step 1: Create .env file
cp .env.example .env

# Step 2: Add required variables
OPENAI_API_KEY=your_key
DEFAULT_OUTPUT_DIR=./output
LOG_LEVEL=INFO

# Step 3: Run
python main.py --run-sample
```

**Affected**: All deployment scripts

**Timeline**: Week 1, Day 2

---

### Breaking Change 2.2: Command-Line Arguments Changed

**What's Changing**:
```bash
# Old CLI (deprecated)
python main.py --emails data.json --output ./results

# New CLI (required)
python main.py extract --emails data.json --output ./results
```

**New subcommands**:
- `extract` - Run extraction pipeline
- `validate` - Validate input data
- `health` - Check system health

**Migration**:
```bash
# Update all scripts
find . -name "*.sh" -exec sed -i 's/python main.py/python main.py extract/g' {} \;
```

**Timeline**: Week 2, Day 1

---

## PHASE 3: API & Data Format Changes

### Breaking Change 3.1: JSON Schema Changes

**What's Changing**:
```json
// Old project intelligence
{
  "project_id": "project_001",
  "project_name": "Test",
  "evidence": ["msg_001"],
  "topics": [{"topic": "API", "evidence": ["msg_001"]}]
}

// New (with validation)
{
  "id": "project_001",  // renamed
  "name": "Test",        // renamed
  "metadata": {          // NEW
    "created_at": "2025-11-17T12:00:00Z",
    "version": "1.0"
  },
  "evidence": {          // structure changed
    "message_ids": ["msg_001"],
    "confidence": 0.95
  },
  "topics": [
    {
      "id": "topic_001",  // NEW - unique ID
      "name": "API",      // renamed from "topic"
      "evidence": {
        "message_ids": ["msg_001"],
        "confidence": 0.90
      }
    }
  ]
}
```

**Impact**: Parsing old JSON files will fail

**Migration Script**:
```python
# scripts/migrate_json_schema.py
def migrate_v1_to_v2(old_json):
    """Migrate old JSON format to new."""
    new_json = {
        "id": old_json["project_id"],
        "name": old_json["project_name"],
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "2.0"
        },
        "evidence": {
            "message_ids": old_json["evidence"],
            "confidence": 1.0  # default
        },
        "topics": [
            {
                "id": f"topic_{hash(t['topic'])}",
                "name": t["topic"],
                "evidence": {
                    "message_ids": t["evidence"],
                    "confidence": 1.0
                }
            }
            for t in old_json.get("topics", [])
        ]
    }
    return new_json

# Usage
python scripts/migrate_json_schema.py --input output/old.json --output output/new.json
```

**Timeline**: Week 3, Day 1

---

### Breaking Change 3.2: Graph Format Changes

**What's Changing**:
- NetworkX node-link format → Custom format
- Added version field
- Added schema validation

**Migration**:
```python
# Load old graph
with open('old_graph.json') as f:
    old_data = json.load(f)

# Convert
new_data = {
    "version": "2.0",
    "schema": "graphmail-v2",
    "nodes": old_data["nodes"],  # compatible
    "edges": old_data["links"],  # renamed from "links"
    "metadata": {
        "created_at": datetime.now().isoformat(),
        "trust_score": calculate_trust_score(old_data)
    }
}

# Save
with open('new_graph.json', 'w') as f:
    json.dump(new_data, f, indent=2)
```

**Timeline**: Week 3, Day 1

---

## PHASE 4: Database Migration

### Breaking Change 4.1: JSON Files → PostgreSQL

**What's Changing**:
- All data moves from JSON files → database
- File-based storage deprecated

**Impact**: 
- `output/` folder no longer used
- Need database connection

**Migration**:
```bash
# Step 1: Set up database
docker-compose up -d postgres

# Step 2: Run migrations
alembic upgrade head

# Step 3: Import existing data
python scripts/migrate_to_db.py --input output/ --db postgres://localhost/graphmail

# Step 4: Verify
python -c "from src.db import get_projects; print(len(get_projects()))"
```

**Rollback Plan**:
```bash
# Export from database back to JSON
python scripts/export_to_json.py --output output_backup/
```

**Timeline**: Week 4, Day 1-2

---

### Breaking Change 4.2: API Endpoints Required

**What's Changing**:
- Direct function calls → REST API calls
- Dashboard must use API

**Impact**: Streamlit dashboard needs rewrite

**Migration**:
```python
# Before (direct import)
from src.workflow import run_pipeline
result = run_pipeline(emails, calendar)

# After (API call)
import requests
response = requests.post(
    "http://localhost:8000/api/v1/extract",
    json={"emails": emails, "calendar": calendar}
)
result = response.json()
```

**Timeline**: Week 4, Day 3

---

## PHASE 5: Dependency Changes

### Breaking Change 5.1: Python Version Requirement

**What's Changing**:
```python
# Old (permissive)
python_requires=">=3.9"

# New (strict)
python_requires="==3.11.*"
```

**Impact**: Python 3.9/3.10 users must upgrade

**Migration**:
```bash
# Use pyenv to install Python 3.11
pyenv install 3.11.7
pyenv local 3.11.7

# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Timeline**: Week 1, Day 1

---

### Breaking Change 5.2: New Required Dependencies

**What's Changing**:
```
# New requirements
sqlalchemy>=2.0.0
alembic>=1.13.0
fastapi>=0.104.0
uvicorn>=0.24.0
redis>=5.0.0
structlog>=23.2.0
tenacity>=8.2.0
```

**Impact**: Larger install footprint (80MB → 200MB)

**Migration**:
```bash
pip install -r requirements.txt
# May take 2-3 minutes
```

**Timeline**: Throughout Weeks 1-4

---

## PHASE 6: Environment Changes

### Breaking Change 6.1: Redis Required for Caching

**What's Changing**:
- Optional caching → Required caching
- Need Redis server

**Impact**: Cannot run without Redis

**Migration**:
```bash
# Option 1: Docker
docker run -d -p 6379:6379 redis:7

# Option 2: Local install
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Option 3: Cloud (production)
# Use Redis Cloud or AWS ElastiCache
```

**Fallback Mode**:
```python
# If Redis unavailable, use in-memory cache (dev only)
CACHE_BACKEND=memory python main.py extract ...
```

**Timeline**: Week 3, Day 2

---

### Breaking Change 6.2: Secrets Manager Required (Production)

**What's Changing**:
- `.env` file → AWS Secrets Manager
- API keys not in environment variables

**Impact**: Production deployments need AWS setup

**Migration**:
```bash
# Step 1: Create secret in AWS
aws secretsmanager create-secret \
    --name prod/graphmail/api-keys \
    --secret-string '{"openai_key": "sk-..."}'

# Step 2: Update deployment config
export SECRETS_MANAGER_ARN=arn:aws:secretsmanager:...

# Step 3: Deploy
kubectl apply -f k8s/deployment.yaml
```

**Timeline**: Week 4+

---

## Deprecation Warnings

### Will Be Removed in v2.0

1. **Deprecated**: Direct Python imports of agents
   - **Use Instead**: API endpoints
   - **Timeline**: Deprecated Week 4, Removed v2.0

2. **Deprecated**: JSON file storage
   - **Use Instead**: Database
   - **Timeline**: Deprecated Week 4, Removed v2.0

3. **Deprecated**: Synchronous LLM calls
   - **Use Instead**: Async API
   - **Timeline**: Deprecated Week 3, Removed v2.0

4. **Deprecated**: `main.py` direct execution
   - **Use Instead**: `graphmail` CLI command
   - **Timeline**: Deprecated Week 2, Removed v2.0

---

## Rollback Procedures

### If Migration Fails

```bash
# 1. Restore from backup
cp -r output_backup/ output/

# 2. Checkout previous version
git checkout v1.0-stable

# 3. Reinstall old dependencies
pip install -r requirements.v1.txt

# 4. Verify
python test_system.py
```

### If Database Corrupted

```bash
# 1. Drop database
dropdb graphmail

# 2. Recreate
createdb graphmail

# 3. Restore from JSON backup
python scripts/migrate_to_db.py --input output_backup/

# 4. Verify
psql graphmail -c "SELECT COUNT(*) FROM projects;"
```

---

## Testing Strategy

### Before Migration
```bash
# 1. Backup everything
tar -czf backup_$(date +%Y%m%d).tar.gz output/ data/ .env

# 2. Run full test suite
pytest tests/ --cov=src

# 3. Document current state
python scripts/document_current_state.py > PRE_MIGRATION_STATE.txt
```

### During Migration
```bash
# Run tests after each phase
pytest tests/migration/test_phase1.py
pytest tests/migration/test_phase2.py
# etc.
```

### After Migration
```bash
# 1. Verify data integrity
python scripts/verify_migration.py

# 2. Run full test suite
pytest tests/

# 3. Performance benchmark
python scripts/benchmark.py --compare PRE_MIGRATION_STATE.txt
```

---

## Communication Plan

### Internal Team
- [ ] Share this document 2 weeks before migration
- [ ] Hold migration planning meeting
- [ ] Assign owners for each phase
- [ ] Set up rollback procedures

### External Users (if open source)
- [ ] Announce in CHANGELOG.md
- [ ] Create migration guide issue
- [ ] Update documentation
- [ ] Provide migration scripts

---

## Timeline Summary

| Phase | Breaking Changes | Timeline | Rollback Risk |
|-------|------------------|----------|---------------|
| Phase 1 | File structure | Week 1 | Low |
| Phase 2 | Configuration | Week 1-2 | Low |
| Phase 3 | Data formats | Week 3 | Medium |
| Phase 4 | Database | Week 4 | High |
| Phase 5 | Dependencies | Week 1-4 | Low |
| Phase 6 | Environment | Week 3-4 | Medium |

**Highest Risk**: Phase 4 (Database migration) - requires extensive testing

---

## Success Criteria

Migration is successful when:
- ✅ All tests pass
- ✅ No data loss
- ✅ Performance improved or maintained
- ✅ Zero production incidents
- ✅ Documentation updated
- ✅ Team trained on new system

---

## Support

**Questions**: Create GitHub issue with `migration` label  
**Urgent Issues**: Contact maintainer directly  
**Rollback Needed**: Run `scripts/rollback.sh --phase [1-6]`

---

**Last Updated**: November 17, 2025  
**Next Review**: Before each phase begins


