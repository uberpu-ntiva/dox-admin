# PACT Feature Coverage Matrix

**Last Updated**: 2025-11-09
**Purpose**: Map all PACT features to existing interfaces and identify gaps

---

## Feature Backlog vs Existing Interfaces

### Legend
- ✅ **Covered** - Interface exists and functional
- ⚠️ **Partial** - Some functionality exists, needs enhancement
- ❌ **Missing** - No interface exists
- 🔄 **In Tools** - Exists in Bridge.DOC/Tools/src
- 📱 **In Gateway** - Exists in dox-gtwy-main/public
- 🔧 **Backend Only** - Service exists, no UI

---

## 1. Document Upload & Detection

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Drag-drop upload | ✅ | 📱 `upload.html` | Gateway dashboard |
| PDF detection | ✅ | 🔧 `dox-tmpl-pdf-recognizer` | OCR backend |
| Template recognition | ✅ | 🔧 `dox-tmpl-pdf-recognizer` | Tesseract + EasyOCR |
| Field detection | ✅ | 🔧 `dox-tmpl-pdf-recognizer` | Auto-classify fields |
| Batch upload | ✅ | 📱 `upload.html` + 🔄 `paste-board` | Multiple files |
| Barcode detection | ⚠️ | 🔧 `dox-rtns-barcode-matcher` + 🔄 `svg-viewer/datamatrix.js` | Backend only, UI partial |

**Gap Analysis**: Barcode UI needs integration with svg-viewer

---

## 2. Field Mapping UI + Mapping to Data Sources

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Visual field mapper | ⚠️ | 🔄 `svg-viewer` | Exists but not integrated |
| Drag-and-drop fields | ⚠️ | 🔄 `svg-viewer/field-utils.js` | Code exists |
| Data source selection | ❌ | - | No UI |
| CRM integration | 🔧 | Backend services | No UI |
| AI field mapping | ✅ | 🔧 `dox-tmpl-field-mapper` | OpenAI backend |
| Field mapping preview | ⚠️ | 🔄 `svg-viewer/view-svg.html` | PDF preview exists |
| Save field maps | ✅ | 🔧 Database | `dbo.TemplateFieldMap` |

**Gap Analysis**:
- Need unified field mapping UI combining svg-viewer + data source selector
- AI mapping works but no UI to trigger/configure

---

## 3. Signer Management + Signature Storage

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Add signers | ⚠️ | Legacy ASPX | DocumentGeneration.aspx Tab 1 |
| Signer email config | ⚠️ | Legacy ASPX | Exists in old system |
| Signature tracking | ✅ | 📱 `esignature.html` | Gateway dashboard |
| AssureSign integration | ✅ | 🔧 `dox-esig-service` | Backend complete |
| DocuSign integration | ❌ | - | Not implemented |
| DocuSeal integration | ❌ | - | Not implemented |
| Signature storage | ✅ | Azure Blob + DB | Backend complete |
| Signer status dashboard | ✅ | 📱 `esignature.html` | Pending/signed/expired |

**Gap Analysis**:
- Signer management UI needs modernization (currently in legacy ASPX)
- DocuSign/DocuSeal integrations missing

---

## 4. Template Bundling & Recipe Builder

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Select multiple templates | ⚠️ | Legacy ASPX | DocumentGeneration.aspx Tab 2 |
| Create bundles ("recipes") | ❌ | - | No UI |
| Save recipe templates | ❌ | - | No backend |
| Bundle preview | ❌ | - | No UI |
| Recipe library | ❌ | - | No UI |

**Gap Analysis**: **CRITICAL MISSING FEATURE**
- No recipe/bundle system exists in modern PACT
- Legacy had multi-select but no saved "recipes"
- Backend needs recipe storage tables
- UI needs recipe builder interface

---

## 5. Batch Sending to Multi-targets

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Paste bulk data | ✅ | 🔄 `paste-board/index.html` | **PasteBlox** interface |
| Parse contracts + tiers | ✅ | 🔄 `paste-board/blokker/` | Contract.js, Tiers.js, Member.js |
| Validate pasted data | ✅ | 🔄 `paste-board/errorListDisplay.js` | Error navigation |
| Batch generation | ✅ | 🔄 `paste-board` + Legacy | Batch.aspx |
| Multi-site targeting | ✅ | Legacy ASPX | DocumentGeneration.aspx |
| Progress tracking | ✅ | 🔄 `paste-board/progressBar.js` | Visual progress |
| Error handling | ✅ | 🔄 `paste-board/errorListDisplay` | Red/green validation |

**Gap Analysis**: **EXCELLENT COVERAGE**
- PasteBlox is sophisticated bulk entry tool
- Needs modernization and integration into PACT gateway
- Backend batch assembly service exists (`dox-batch-assembly`)

---

## 6. Manual Return: Scan Upload + OCR

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Scan upload | ✅ | 📱 `dox-rtns-manual-upload` | 4 HTML interfaces |
| PDF OCR processing | ✅ | 🔧 `dox-tmpl-pdf-recognizer` | Tesseract + EasyOCR |
| Document classification | ⚠️ | 🔧 Backend logic | No UI |
| Match to contracts | ⚠️ | 🔧 Logic exists | No UI |
| Error resolution | ✅ | 📱 `dox-rtns-manual-upload/errors.html` | Manual intervention |
| Batch status | ✅ | 📱 `dox-rtns-manual-upload/status.html` | Real-time tracking |

**Gap Analysis**:
- Good coverage, needs better document classification UI
- Match confidence scoring UI needed

---

## 7. Barcode Matching System

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Barcode scanning | ⚠️ | 🔄 `svg-viewer/datamatrix.js` | Lib exists |
| QR code detection | ⚠️ | 🔄 `svg-viewer/datamatrix.js` | DataMatrix support |
| Match to records | ✅ | 🔧 `dox-rtns-barcode-matcher` | Backend service |
| Barcode generation | ❌ | - | No UI |
| Barcode validation UI | ❌ | - | No UI |

**Gap Analysis**: **PARTIALLY IMPLEMENTED**
- DataMatrix library exists but not integrated
- Barcode matcher service exists
- Need UI for barcode management

---

## 8. External Signing (DocuSign/DocuSeal Integration)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| AssureSign | ✅ | 🔧 `dox-esig-service` | Complete |
| DocuSign | ❌ | - | Not implemented |
| DocuSeal | ❌ | - | Not implemented |
| Provider selection | ❌ | - | No UI |
| Webhook handling | ✅ | 🔧 `dox-esig-webhook-listener` | AssureSign only |

**Gap Analysis**: **CRITICAL MISSING**
- Only AssureSign implemented
- Need DocuSign/DocuSeal adapters
- Need provider selection UI

---

## 9. Price Activation Flow (Submit → Response → Retry)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Submit price activation | ⚠️ | Legacy | Mentioned in pact-project-desc.md |
| Async feedback handling | ❌ | - | No implementation |
| Retry logic | ❌ | - | No implementation |
| Status dashboard | ❌ | - | No UI |
| Response tracking | ❌ | - | No backend |

**Gap Analysis**: **CRITICAL MISSING FEATURE**
- Price activation workflow not implemented
- No backend service for price activation
- No UI for submission or tracking

---

## 10. Activation Appeals System

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Submit appeal | ❌ | - | Not implemented |
| Appeal tracking | ❌ | - | Not implemented |
| Appeal approval workflow | ❌ | - | Not implemented |
| Status dashboard | ❌ | - | Not implemented |

**Gap Analysis**: **COMPLETELY MISSING**
- Entire appeals system not implemented

---

## 11. Distributor Relationship Manager (Parent/Child)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Account hierarchy view | ✅ | 🔄 `accounts-tbl-hier` | Tree view exists |
| Parent-child linking | ⚠️ | 🔄 `accounts-tbl-hier` | UI exists, needs backend |
| Relationship validation | ❌ | - | No logic |
| Hierarchy visualization | ✅ | 🔄 `accounts-tbl-hier` | Good UI |

**Gap Analysis**: **UI EXISTS, BACKEND NEEDED**
- accounts-tbl-hier has good hierarchical interface
- Needs backend service for distributor relationships
- Database schema may exist in legacy

---

## 12. Tier Elevation Engine (auto + request)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Tier paste board | ✅ | 🔄 `tiers-pb` + `paste-board/blokker/Tiers.js` | UI exists |
| Auto tier calculation | ❌ | - | No logic |
| Manual tier request | ⚠️ | Legacy | May exist in old system |
| Tier approval | ❌ | - | No workflow |
| Tier history | ❌ | - | No tracking |

**Gap Analysis**: **UI EXISTS, LOGIC MISSING**
- Tier UI components exist (PasteBlox tiers)
- Auto elevation logic not implemented
- Approval workflow missing

---

## 13. Contract Rollover Tracker

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Contract expiration tracking | ⚠️ | 🔧 `dox-auto-lifecycle-service` | Lifecycle service |
| Rollover notifications | ❌ | - | Not implemented |
| Rollover UI | ❌ | - | Not implemented |
| Renewal workflow | ❌ | - | Not implemented |

**Gap Analysis**: **PARTIALLY IMPLEMENTED**
- Lifecycle service tracks document retention
- Contract-specific rollover logic missing
- No UI for rollover management

---

## 14. ETL System for Purchase Feed Imports

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| ETL service | ✅ | 🔧 `dox-data-etl-service` | Backend exists |
| Feed configuration | ❌ | - | No UI |
| Import status | ⚠️ | 📱 Logs? | No dedicated UI |
| Error handling | ⚠️ | Backend | No UI |
| Data mapping | ❌ | - | No UI |
| Schedule management | ❌ | - | No UI |

**Gap Analysis**: **BACKEND EXISTS, UI MISSING**
- ETL service exists but no admin UI
- Need configuration interface
- Need monitoring dashboard

---

## 15. Coverage Zone Tracking (Active / Pending / In Construction)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Zone mapping | ❌ | - | Not implemented |
| Status tracking | ❌ | - | Not implemented |
| Geographic visualization | ❌ | - | Not implemented |
| Zone assignment | ❌ | - | Not implemented |

**Gap Analysis**: **COMPLETELY MISSING**
- Entire coverage zone system not implemented
- May need mapping library (Leaflet, Google Maps)

---

## 16. Workflow Automation Engine (Trigger → Condition → Action)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Workflow engine | ✅ | 🔧 `dox-auto-workflow-engine` | Backend exists |
| Workflow builder UI | ⚠️ | 📱 `workflows.html` | Basic interface |
| Trigger configuration | ❌ | - | No UI |
| Condition builder | ❌ | - | No UI |
| Action configuration | ❌ | - | No UI |
| Workflow testing | ❌ | - | No UI |

**Gap Analysis**: **BACKEND EXISTS, UI BASIC**
- Workflow engine backend complete
- Visual workflow builder needed (like n8n/Zapier)
- workflows.html exists but needs enhancement

---

## 17. Transaction Audit Logs + Snapshot Comparison

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Audit logging | ✅ | 🔧 `dox-actv-service` + listener | Backend complete |
| Audit log UI | ✅ | 📱 `audit-log.html` | Gateway dashboard |
| Snapshot capture | ❌ | - | Not implemented |
| Comparison UI | ❌ | - | Not implemented |
| Version history | ❌ | - | Not implemented |

**Gap Analysis**: **AUDIT LOGS DONE, SNAPSHOTS MISSING**
- Activity tracking complete
- audit-log.html provides filtering
- Snapshot/diff comparison not implemented

---

## 18. Admin Portal (Rules, Chargebacks, Enforcement Policies)

| Sub-Feature | Status | Location | Notes |
|-------------|--------|----------|-------|
| Settings UI | ✅ | 📱 `settings.html` | Gateway dashboard |
| Rules engine | ❌ | - | Not implemented |
| Chargeback management | ❌ | - | Not implemented |
| Policy editor | ❌ | - | Not implemented |
| Admin user management | ✅ | 📱 `users.html` | Basic CRUD |

**Gap Analysis**: **BASIC ADMIN EXISTS, ADVANCED MISSING**
- Basic admin (settings, users) exists
- Rules engine, chargebacks, policies not implemented

---

## Summary: Coverage Analysis

### ✅ Well Covered (10 features)
1. Document Upload & Detection
2. Batch Sending (PasteBlox)
3. Manual Return Processing
4. Signer Status Tracking
5. Audit Logging
6. User Management
7. ETL Backend (no UI)
8. Workflow Engine Backend
9. Account Hierarchy UI
10. Template Recognition (OCR)

### ⚠️ Partially Covered (7 features)
1. Field Mapping (code exists, needs integration)
2. Signer Management (legacy only)
3. Barcode System (lib exists, not integrated)
4. Contract Rollover (lifecycle only)
5. Tier Elevation (UI exists, logic missing)
6. Distributor Relationships (UI exists, backend needed)
7. Workflow Builder (basic UI, needs visual builder)

### ❌ Missing (9 features)
1. **Template Bundling/Recipe Builder** - CRITICAL
2. **Price Activation Flow** - CRITICAL
3. **Activation Appeals System** - CRITICAL
4. **DocuSign/DocuSeal Integration** - HIGH PRIORITY
5. **Coverage Zone Tracking** - MEDIUM
6. **Rules Engine** - MEDIUM
7. **Chargeback Management** - MEDIUM
8. **Snapshot Comparison** - LOW
9. **Workflow Visual Builder** - MEDIUM

---

## Modernization Opportunities

### Bridge.DOC Tools to Integrate

**HIGH VALUE**:
1. **paste-board** (PasteBlox) → Integrate into Gateway
   - Bulk contract/tier entry with validation
   - Error navigation and correction
   - Progress tracking
   - Already sophisticated and functional

2. **svg-viewer** → Integrate into Template UI
   - PDF field visualization
   - Datamatrix barcode support
   - Field editing interface

3. **accounts-tbl-hier** → Integrate into Users/Accounts
   - Hierarchical account management
   - Parent-child relationships
   - Tree visualization

**MEDIUM VALUE**:
4. **taxi** → Data import tool
   - Yellow Pages scraping
   - External data ingestion
   - Could enhance ETL UI

5. **contract-lookup** → Search interface
   - Contract search
   - Could enhance Documents UI

6. **tiers-pb** → Tier management
   - Tier paste board
   - Complement to PasteBlox

---

## Recommended Implementation Priority

### Phase 1: Critical Gaps (MVP Blockers)
1. **Template Bundling/Recipe Builder** - Core feature
2. **Price Activation Flow** - Business critical
3. **DocuSign Integration** - Market requirement
4. **Field Mapping Integration** - Complete svg-viewer integration

### Phase 2: High-Value Integrations
5. **PasteBlox Integration** - Move to PACT gateway
6. **Barcode System Completion** - Integrate datamatrix.js
7. **Visual Workflow Builder** - Enhance workflows.html
8. **Tier Elevation Logic** - Complete tier system

### Phase 3: Advanced Features
9. **Activation Appeals System**
10. **Coverage Zone Tracking**
11. **Rules Engine**
12. **Snapshot Comparison**

### Phase 4: Administrative Enhancements
13. **Chargeback Management**
14. **Advanced Reporting**
15. **Compliance Features**

---

## Next Steps

1. **Set up Next.js preview in test-jules** - Prototype new UIs
2. **Port PasteBlox to modern stack** - Highest ROI
3. **Build Recipe Builder** - Critical missing feature
4. **Integrate svg-viewer** - Complete field mapping
5. **Implement Price Activation** - Business requirement

---

**Document Status**: Complete feature analysis
**Last Review**: 2025-11-09
**Next Review**: After Phase 1 implementation
