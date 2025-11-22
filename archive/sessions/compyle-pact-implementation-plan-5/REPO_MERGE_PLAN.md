# Repository Merge Plan: pact-manual-upload → rtns-manual-upload

**Date**: 2025-11-09
**Decision**: Merge dox-pact-manual-upload into dox-rtns-manual-upload (target)

---

## Analysis Summary

### File Comparison

| File | pact size | rtns size | Difference |
|------|-----------|-----------|------------|
| app/app.py | 59,179 bytes (1,348 lines) | 63,421 bytes (1,442 lines) | rtns is larger (+94 lines) |
| app/database.py | 15,683 | 15,683 | Identical |
| app/models.py | 26,224 | 26,224 | Identical |
| app/ocr_utils.py | 17,509 | 17,509 | Identical |
| app/pdf_utils.py | 10,084 | 10,084 | Identical |
| app/sharepoint_client.py | 14,165 | 14,165 | Identical |
| app/validators.py | 8,553 | 8,553 | Identical |
| app/exceptions.py | 2,533 | 2,533 | Identical |

### Conclusion

**95% Duplicate**: Only `app.py` differs (rtns version is more complete)

**Reason**: Both services handle manual document upload but were created with different names:
- `dox-pact-manual-upload`: Legacy naming (PACT project name)
- `dox-rtns-manual-upload`: Returns processing (correct naming)

---

## Merge Strategy

### Keep: dox-rtns-manual-upload ✅
**Reasons**:
- Larger app.py (more features)
- Better naming (returns = "rtns")
- Marked as "Active (Ported)" in docs
- More complete implementation

### Deprecate: dox-pact-manual-upload ❌
**Reasons**:
- Smaller codebase
- Legacy naming
- Redundant functionality

---

## Migration Steps

### 1. Code Review (Already Done)
✅ Analyzed differences
✅ Confirmed rtns version is more complete
✅ Verified no unique features in pact version

### 2. Update Gateway Routes

**File**: `dox-gtwy-main/config.py`

```python
# REMOVE THIS:
# 'dox-pact-manual-upload': {
#     'url': PACT_UPLOAD_SERVICE_URL,
#     'timeout': 60,
# }

# KEEP THIS:
'dox-rtns-manual-upload': {
    'url': RTNS_UPLOAD_SERVICE_URL,
    'timeout': 60,
    'auth_required': True,
    'rate_limit': (100, 60),
}
```

### 3. Update Gateway Routes

**File**: `dox-gtwy-main/app.py`

```python
# Update all references:
# OLD: /api/pact-upload/*
# NEW: /api/rtns-upload/*

@app.route('/api/returns/upload', methods=['POST'])
def upload_return_document():
    """Upload returned document (consolidated endpoint)"""
    response, content, status = proxy_request('dox-rtns-manual-upload', 'api/upload')
    return jsonify(content), status
```

### 4. Update Docker Compose

**File**: `DOX/docker-compose.yml`

```yaml
# REMOVE this service:
# dox-pact-manual-upload:
#   build: ./dox-pact-manual-upload
#   container_name: pact-manual-upload
#   ports:
#     - "5011:5000"

# KEEP this service:
dox-rtns-manual-upload:
  build: ./dox-rtns-manual-upload
  container_name: rtns-manual-upload
  ports:
    - "5010:5000"
  environment:
    - FLASK_ENV=development
    - DATABASE_URL=${DATABASE_URL}
    - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
```

### 5. Update Service Registry

**File**: `dox-admin/strategy/SERVICES_REGISTRY.md`

```markdown
## Upload Services

### dox-rtns-manual-upload ✅ ACTIVE
**Status**: Active (Ported)
**Port**: 5010
**Purpose**: Manual upload of returned signed documents
**Interfaces**: 4 HTML pages (upload, batch, status, errors)

### ~~dox-pact-manual-upload~~ ❌ DEPRECATED
**Status**: Deprecated (merged into dox-rtns-manual-upload)
**Date Deprecated**: 2025-11-09
**Reason**: Duplicate of rtns-manual-upload
```

### 6. Update Documentation

Files to update:
- `DOX/README.md` - Remove pact-manual-upload references
- `DOX/PACT_SYSTEM_STATUS_REPORT.md` - Mark as deprecated
- `dox-gtwy-main/README.md` - Update service list

### 7. Archive Repository (DO NOT DELETE)

```bash
# Move to archive directory
mkdir -p DOX/archives/deprecated-services
mv dox-pact-manual-upload DOX/archives/deprecated-services/
echo "Merged into dox-rtns-manual-upload on 2025-11-09" > DOX/archives/deprecated-services/dox-pact-manual-upload/DEPRECATED.txt
```

---

## Testing Checklist

After merge:

- [ ] Gateway can route to rtns-manual-upload
- [ ] Upload endpoint works: `POST /api/returns/upload`
- [ ] Batch upload works
- [ ] Status tracking works
- [ ] Error handling works
- [ ] All 4 HTML pages load correctly
- [ ] Docker compose starts without pact service
- [ ] No broken references in gateway logs

---

## Rollback Plan

If issues arise:

1. Restore pact-manual-upload from archive
2. Re-add to docker-compose.yml
3. Re-enable gateway routes
4. Investigate differences

---

## Impact Assessment

### Services Affected
- ✅ dox-gtwy-main (gateway routes updated)
- ✅ dox-rtns-manual-upload (no changes needed)
- ❌ dox-pact-manual-upload (deprecated)

### Zero Impact Areas
- All other backend services (no dependencies)
- Database schema (unchanged)
- Frontend (uses gateway routes, transparent change)
- Azure Blob Storage (same container)

### Risk Level: **LOW**
- Functionality already exists in rtns
- No unique features lost
- Simple route update in gateway

---

## Timeline

- **Analysis**: ✅ Complete
- **Plan Creation**: ✅ Complete
- **Gateway Updates**: ⏳ Ready to implement
- **Docker Compose Update**: ⏳ Ready to implement
- **Testing**: ⏳ After implementation
- **Archive**: ⏳ After successful test

**Estimated Time**: 30 minutes

---

## Approval Status

- [x] Technical analysis complete
- [x] No unique features in deprecated repo
- [x] Merge plan documented
- [ ] Gateway updates ready
- [ ] Testing plan ready
- [ ] Approved for implementation

**Next Step**: Update gateway configuration and docker-compose
