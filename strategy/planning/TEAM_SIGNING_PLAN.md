# Signing Team Plan

**Team**: Signing
**Services Owned**: dox-esig-service, dox-esig-webhook-listener, dox-rtns-manual-upload
**Phase**: Phase 2 Week 2
**Status**: Planning (T06 - Port dox-rtns-manual-upload)

---

## Team Composition

| Role | Agent/Person | Responsibilities |
|------|---|---|
| Lead | Agent-Signing-Lead | E-signature coordination |
| E-Sig Dev | Agent-ESig-Dev | Maintain dox-esig-service |
| Webhook Handler | Agent-Webhook-Dev | Maintain dox-esig-webhook-listener |
| Returns Dev | Agent-Returns-Dev | Maintain dox-rtns-manual-upload |

---

## Services Owned

### dox-esig-service
- **Purpose**: E-signature integration (Nintex AssureSign)
- **Status**: Active
- **Dependencies**: dox-core-auth, AssureSign API
- **Phase 2 Priority**: P2

### dox-esig-webhook-listener
- **Purpose**: Receive webhook callbacks from AssureSign
- **Status**: Active
- **Phase 2 Priority**: P2

### dox-rtns-manual-upload
- **Purpose**: Returns document processing
- **Status**: Ready for T06 porting
- **Dependencies**: dox-core-store, dox-core-auth, dox-tmpl-service
- **Phase 2 Priority**: P1 (Critical - T06 task)

---

## Week 2 Deliverables

### Must Complete (T06 - Porting)
- [ ] Complete porting of dox-rtns-manual-upload from dox-pact-manual-upload
- [ ] Update all naming conventions (pact → rtns)
- [ ] Verify document processing workflow works
- [ ] Register service in SERVICES_REGISTRY.md
- [ ] Create SERVICE_dox-rtns-manual-upload.json

### Should Complete
- [ ] E-signature workflow integration
- [ ] Webhook endpoint testing
- [ ] Memory bank coordination

### Nice to Have
- [ ] Advanced signing templates
- [ ] Multi-party signing support
- [ ] Digital certificate management

---

## T06: Service Porting Details

**Source**: dox-pact-manual-upload (PACT return processing)
**Target**: dox-rtns-manual-upload (RTNS return processing)
**Method**: Copy with naming updates per SERVICE_TEMPLATE structure

### Porting Checklist
- [ ] Apply SERVICE_TEMPLATE structure
- [ ] Update class names: PactReturn → RtnsReturn
- [ ] Update route prefixes: /api/pact → /api/rtns
- [ ] Update port: 5001 → 5003
- [ ] Update database schema references
- [ ] Update SharePoint endpoint URLs
- [ ] Update logging/telemetry references
- [ ] Run integration tests
- [ ] Update documentation

---

## Cross-Team Dependencies

**Upstream Dependencies**:
- Infrastructure Team: dox-core-auth, dox-core-store
- Document Team: dox-tmpl-service for document types

**Downstream Dependents**:
- Activation Team: Signs and activates returns
- Automation Team: Workflow routing for signed documents

**Status**: Ready to proceed with T06 porting

---

## Resource Allocation

- **Dev Time**: 40% T06 porting, 30% integration, 30% testing
- **T06 Effort**: Estimated 3-5 days
- **Testing**: Full regression test suite

---

## Integration Points

```
Manual Returns Upload
    ↓
dox-rtns-manual-upload (Process)
    ↓
Validate with templates → Extract fields
    ↓
Submit for E-Signature via dox-esig-service
    ↓
Receive signed → Webhook to dox-esig-webhook-listener
    ↓
Update document status
```

---

## Success Metrics

- T06 porting complete with zero functionality loss
- Document processing accuracy > 98%
- E-signature integration working
- Webhook delivery success rate > 99.9%
- All integration tests passing

---

**Team Status**: Ready for T06
**Priority**: P1 (Blocking)
**Next Sync**: Monday 9 AM UTC
**Memory Bank**: TEAM_Signing.json
