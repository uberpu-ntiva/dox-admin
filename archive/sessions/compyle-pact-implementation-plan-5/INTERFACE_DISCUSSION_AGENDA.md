# Interface Discussion Agenda
**For Next Session**
**Date Prepared:** 2025-11-09

---

## Opening Context

User explicitly requested: "Have the next chat begin about interfaces."

This document provides a structured agenda for the interface discussion, based on:
1. Work completed in this session (4 new preview components)
2. Discovery of 13 Bridge.DOC Tools interfaces
3. Hybrid interface architecture confirmed (centralized + service-specific)
4. Critical missing features identified (Price Activation, Recipe Builder)

---

## Agenda Overview

1. Review Preview Components [15 min]
2. Bridge.DOC Tools Evaluation [20 min]
3. Technology Stack Decision [15 min]
4. Integration Architecture [20 min]
5. Implementation Priorities [15 min]
6. User Experience Flows [15 min]
7. Next Steps & Action Items [10 min]

**Total Estimated Time:** ~2 hours

---

## 1. Review Preview Components

### Purpose
Show user the 6 completed preview components and get feedback on design, functionality, and priorities.

### Discussion Points

#### 1.1 Field Mapper
**Preview:** `/field-mapper/page.tsx`

**Questions:**
- Does the visual field positioning match your expectations?
- Should we integrate OCR auto-detection first, or allow manual placement only?
- Field types: Are text, signature, checkbox, date, email sufficient, or need more?
- Should field properties include validation rules (regex, min/max length, etc.)?

**Implementation Decisions:**
- Keep React version from preview or port svg-viewer vanilla JS?
- Integration point: When does OCR run? (on upload, on demand, background process?)
- Storage: Where do field coordinates live? (TemplateFieldMap table confirmed)

#### 1.2 Price Activation
**Preview:** `/price-activation/page.tsx`

**Questions:**
- Does the Submit → Track → Retry workflow match your business process?
- How many retries are appropriate? (preview shows 3, configurable?)
- What triggers a price activation? (contract signed, manual submission, bulk upload?)
- Who receives notifications when submissions fail after max retries?

**Implementation Decisions:**
- Backend service required (dox-price-activation-service) - confirm priority
- External API integration: What system receives pricing? (SAP, custom, other?)
- Retry strategy: Exponential backoff intervals? (1min, 5min, 30min, etc.)
- Webhook vs polling for status updates?

#### 1.3 Account Hierarchy
**Preview:** `/accounts/page.tsx`

**Questions:**
- Tree depth: How many levels of parent-child relationships? (preview shows 2, need more?)
- Should revenue roll up from children to parent automatically?
- Can child accounts have different tiers than parent?
- What actions should be available from tree view? (edit, view contracts, add child, etc.)

**Implementation Decisions:**
- Port accounts-tbl-hier from Bridge.DOC or build new React component?
- Backend: dox-actv-service already handles accounts? Or new service needed?
- Database: Recursive queries for hierarchy traversal or materialized path?

#### 1.4 Tier Elevation
**Preview:** `/tiers/page.tsx`

**Questions:**
- Tier structure: Bronze → Silver → Gold → Platinum correct? Or different tiers?
- Eligibility rules: Who defines requirements? (admin configurable or hardcoded?)
- Automatic elevation: Should it be fully automatic or require confirmation?
- Manual requests: What's the approval workflow? (single approver, multi-level, business rules?)

**Implementation Decisions:**
- Extend tiers-pb from Bridge.DOC or build new?
- Rules engine: Database-driven or code-based logic?
- Notification system: Email, in-app, or both when eligible?
- Demotion: What happens if requirements no longer met?

#### 1.5 PasteBlox (Already Previewed)
**Preview:** `/pasteboard/page.tsx`

**Confirmation:**
- This is highest-value Bridge.DOC Tool - confirm priority for porting
- Validation rules: Tab-delimited format, required fields, data types
- Bulk size: What's max rows to support? (100, 1000, 10000?)

#### 1.6 Recipe Builder (Already Previewed)
**Preview:** `/recipe-builder/page.tsx`

**Confirmation:**
- Critical missing feature - confirm Phase 1 priority
- Template ordering: Does order matter for generation? (yes/no)
- Versioning: Should recipes be versioned like templates?

---

## 2. Bridge.DOC Tools Evaluation

### 13 Tools Found in `DOX/Dox.BlueSky/distro/Bridge.DOC/Tools/src/`

#### ✅ Already Previewed (4 tools)
1. **paste-board** (PasteBlox) - Bulk entry
2. **svg-viewer** (Field Mapper) - PDF field mapping
3. **accounts-tbl-hier** (Account Hierarchy) - Tree view
4. **tiers-pb** (Tier Elevation) - Tier management

#### ❓ Need Evaluation (9 tools)

### 2.1 High-Priority Evaluation

#### taxi (Tax Administration)
**Purpose:** Unknown - need to investigate
**Questions:**
- What tax functionality does this provide?
- Is it used in production?
- Does PACT need tax administration features?

**Action:** Show user tool, decide port/skip/redesign

#### otto-form (Template Builder)
**Purpose:** Likely template creation/editing
**Questions:**
- How does this differ from Recipe Builder?
- Is this for PDF template creation or form field mapping?
- Should we merge this with Field Mapper?

**Action:** Evaluate overlap with existing tools, decide integration strategy

#### contract-lookup
**Purpose:** Contract search/retrieval
**Questions:**
- Is this redundant with gateway search functionality?
- What special features does it have?
- Worth porting or enhancing existing search?

**Action:** Compare with gateway search, decide if unique value exists

### 2.2 Medium-Priority Evaluation

#### reports
**Purpose:** Report generation
**Questions:**
- What reports does it generate?
- Is this ad-hoc reporting or pre-defined reports?
- Does PACT have any reporting now?

**Action:** List available reports, prioritize which to implement

#### workflow-builder
**Purpose:** Workflow configuration
**Questions:**
- How does this relate to dox-auto-workflow-engine?
- Is this visual workflow builder (drag-and-drop)?
- Who uses it? (admins only or end users?)

**Action:** Evaluate if dox-auto-workflow-engine needs UI

#### batch-processing
**Purpose:** Batch operations
**Questions:**
- What batch operations does it support?
- Is this document batch generation or data processing?
- Overlap with PasteBlox?

**Action:** Map batch operations, decide if new tool or integrate into existing

### 2.3 Lower-Priority Evaluation

#### document-viewer
**Purpose:** Document viewing
**Questions:**
- Is this just PDF.js wrapper or more?
- What features beyond basic PDF viewing?
- Redundant with Field Mapper's PDF display?

**Action:** Quick review, likely skip if basic PDF.js

#### signature-capture
**Purpose:** Signature capture
**Questions:**
- Is this redundant with AssureSign/DocuSeal integration?
- Any use case for local signature capture?

**Action:** Likely skip, already using external e-signature services

#### pdf-generator
**Purpose:** PDF generation
**Questions:**
- How does this differ from document generation in dox-tmpl-service?
- Is this for merging, splitting, or generating from scratch?

**Action:** Evaluate if features needed beyond existing generation

---

## 3. Technology Stack Decision

### Current State
- **Gateway Frontend:** Vanilla JavaScript ES6+
- **Bridge.DOC Tools:** Vanilla JS + jQuery + Tabulator.js
- **Preview Environment:** Next.js 15 + TypeScript + Tailwind CSS
- **Backend Services:** Python Flask microservices

### Option A: React/Next.js for All New Interfaces

**Pros:**
- Modern developer experience
- Component reusability (use preview components as-is)
- TypeScript for type safety
- Large ecosystem (React Query, Zustand, etc.)
- Easier to find developers with React skills
- Better testing tools (React Testing Library)

**Cons:**
- Requires build step and bundling
- Larger bundle sizes than vanilla JS
- Inconsistency with existing gateway frontend
- May be overkill for simple interfaces

**Best For:**
- Complex UIs (Field Mapper, Recipe Builder, Price Activation)
- New features being built from scratch
- Interfaces requiring frequent updates

### Option B: Vanilla JS for Consistency

**Pros:**
- Consistent with existing gateway
- Matches Bridge.DOC Tools architecture
- No build step required
- Smaller bundle sizes
- Can integrate existing Bridge.DOC code directly

**Cons:**
- More code to write (no component framework)
- Harder to maintain complex state
- Testing more difficult
- Preview components would need to be rewritten

**Best For:**
- Porting existing Bridge.DOC Tools as-is
- Simple CRUD interfaces
- Lightweight integrations

### Option C: Hybrid Approach (RECOMMENDED)

**Strategy:**
- **Centralized Dashboard:** Keep vanilla JS (existing)
- **Complex New Features:** React/Next.js (Price Activation, Recipe Builder)
- **Bridge.DOC Ports:** Keep vanilla JS (PasteBlox, Field Mapper base)
- **Future Interfaces:** React/Next.js by default

**Integration:**
- iframes for embedding React apps in gateway
- Microfrontend architecture with Module Federation
- Or: Full page navigation (simpler, less integration complexity)

**Pros:**
- Best of both worlds
- Gradual migration path
- Can reuse preview components for new features
- Can port Bridge.DOC tools without rewriting

**Cons:**
- Two codebases to maintain
- Need integration layer between vanilla and React
- Team needs skills in both

### Decision Point
**User should decide:** React, Vanilla JS, or Hybrid?

---

## 4. Integration Architecture

### 4.1 Centralized Dashboard ↔ Service UIs

#### Current State
**Centralized Dashboard:** `dox-gtwy-main/public/`
- Vanilla JS frontend
- Communicates with gateway API
- Provides navigation to services

**Service-Specific UIs:**
- dox-tmpl-pdf-recognizer: `upload.html`, `results.html`
- dox-rtns-manual-upload: 4 HTML files
- Bridge.DOC Tools: 13 standalone tools

#### Integration Options

##### Option 1: iframe Embedding
**How it works:**
- Dashboard has iframes for service UIs
- Service UIs communicate with parent via postMessage
- Authentication token passed via message or query param

**Pros:**
- Isolation (no CSS/JS conflicts)
- Easy to implement
- Can load different frameworks

**Cons:**
- iframe overhead
- Awkward for full-page experiences
- Mobile unfriendly

**Best for:** Small embedded widgets, legacy tool integration

##### Option 2: Microfrontend (Module Federation)
**How it works:**
- Each UI is separate build
- Loaded dynamically at runtime
- Share common dependencies (React, etc.)

**Pros:**
- True separation of concerns
- Independent deployments
- Can share libraries

**Cons:**
- Complex setup
- Requires Webpack 5 / Vite
- Steep learning curve

**Best for:** Large teams, many interfaces, long-term scalability

##### Option 3: Full Page Navigation
**How it works:**
- Dashboard links to separate apps (different URLs)
- Each service UI is standalone SPA or MPA
- Session token in localStorage or cookie

**Pros:**
- Simple to implement
- Clean separation
- Easy to reason about

**Cons:**
- Full page reloads
- Can't embed in dashboard
- Navigation feels less integrated

**Best for:** Simple architecture, fast implementation

##### Option 4: API Gateway + Client-side Routing (SPA)
**How it works:**
- Single React app for entire frontend
- Gateway serves API only (no HTML)
- Client-side routing with React Router

**Pros:**
- Modern SPA experience
- Fast navigation (no page reloads)
- Clean architecture

**Cons:**
- Requires rewriting entire frontend
- Loses existing gateway frontend
- Big migration effort

**Best for:** Greenfield project or full rewrite

### Decision Point
**User should decide:** Which integration architecture?

**Recommendation:** Start with Option 3 (Full Page Navigation) for simplicity, migrate to Option 2 (Microfrontend) if scalability needed.

---

### 4.2 Authentication & Authorization

#### Current State
- JWT tokens (15min access, 7day refresh)
- Planned: OAuth2 / Azure B2C migration

#### Questions
1. How do service UIs get authentication token?
   - Query param (less secure)
   - Cookie (requires same domain)
   - localStorage (SPA approach)
   - postMessage from parent (iframe approach)

2. Do different interfaces need different permissions?
   - Role-based access control (RBAC)?
   - Permission per interface?
   - Permission per action within interface?

3. Multi-tenancy (siteId)?
   - Should interfaces be siteId-aware?
   - Do different sites see different interfaces?

### Decision Point
**User should clarify:** Authentication strategy for interfaces

---

### 4.3 API Communication

#### Current State
- Services expose REST APIs (Flask)
- Gateway proxies requests

#### Questions
1. Should interfaces call gateway API or services directly?
   - Gateway proxy (current, recommended for security)
   - Direct service calls (faster, but requires CORS)

2. REST, GraphQL, or tRPC?
   - REST (current, simple, well-understood)
   - GraphQL (flexible queries, reduces over-fetching)
   - tRPC (type-safe, but requires TypeScript on backend)

3. Real-time updates?
   - Polling (simple, higher load)
   - WebSockets (real-time, more complex)
   - Server-Sent Events (one-way, simpler than WebSockets)

**Best for:** Price Activation status updates, workflow progress

### Decision Point
**User should decide:** API communication strategy

**Recommendation:** Stick with REST + Gateway proxy, add WebSockets for Price Activation only

---

## 5. Implementation Priorities

### Proposed Roadmap

#### Phase 1: Critical Missing Features (2-3 weeks)
**Priority:** HIGHEST - Blocks production

1. **Price Activation Service + UI** (NEW)
   - Backend: dox-price-activation-service (Python Flask)
   - Database: PriceSubmissions, SubmissionItems, SubmissionLog
   - UI: Port from preview environment (React)
   - Queue: Celery for retry logic
   - Integration: Webhook from dox-esig-service (contract signed event)
   - Time Estimate: 5-7 days

2. **Recipe Builder Service + UI** (NEW)
   - Backend: Extend dox-tmpl-service
   - Database: TemplateRecipes, RecipeTemplates
   - UI: Port from preview environment (React)
   - Features: CRUD recipes, order templates, preview
   - Integration: Template creation workflow
   - Time Estimate: 4-5 days

**Deliverable:** Price Activation operational, Recipe Builder functional

---

#### Phase 2: Port High-Value Bridge.DOC Tools (2-3 weeks)
**Priority:** HIGH - User experience improvements

1. **PasteBlox** (Port from Bridge.DOC)
   - Source: `Bridge.DOC/Tools/src/paste-board/`
   - Backend: dox-rtns-manual-upload (already exists)
   - UI: Port vanilla JS or rewrite React? (decide in this session)
   - Features: Tab-delimited paste, validation, bulk submit
   - Time Estimate: 3-4 days

2. **Field Mapper Enhanced** (Build on svg-viewer)
   - Source: `Bridge.DOC/Tools/src/svg-viewer/`
   - Backend: dox-tmpl-pdf-recognizer (OCR integration)
   - UI: Enhance with OCR auto-detect
   - Features: PDF upload, OCR, field placement, save template
   - Time Estimate: 4-5 days

3. **Account Hierarchy** (Port accounts-tbl-hier)
   - Source: `Bridge.DOC/Tools/src/accounts-tbl-hier/`
   - Backend: dox-actv-service
   - UI: Port Tabulator.js tree or use React tree library?
   - Features: Expandable tree, parent-child, CRUD accounts
   - Time Estimate: 2-3 days

**Deliverable:** PasteBlox operational, Field Mapper with OCR, Account Hierarchy

---

#### Phase 3: Enhanced Management Interfaces (2-3 weeks)
**Priority:** MEDIUM - Operational improvements

1. **Tier Elevation** (Enhance tiers-pb)
   - Source: `Bridge.DOC/Tools/src/tiers-pb/`
   - Backend: New tables + rules engine
   - UI: Port from preview (React)
   - Features: Auto-eligibility, manual requests, approval workflow
   - Time Estimate: 3-4 days

2. **Admin Dashboard** (NEW)
   - Backend: Aggregate data from multiple services
   - UI: New React dashboard
   - Features: System stats, user management, configuration
   - Time Estimate: 5-7 days

3. **Document Upload Enhanced** (Improve existing)
   - Backend: Existing services
   - UI: Better UX with drag-and-drop, progress bars
   - Features: Batch upload, preview, metadata entry
   - Time Estimate: 3-4 days

**Deliverable:** Tier Elevation operational, Admin Dashboard, Upload UX improved

---

#### Phase 4: Remaining Bridge.DOC Tools (1-2 weeks)
**Priority:** LOWER - Evaluate need first

1. Evaluate 9 remaining tools (see Section 2.2)
2. Port selected high-value tools
3. Skip redundant tools

**Deliverable:** All useful Bridge.DOC functionality available in PACT

---

### Decision Points
1. Confirm Phase 1 is correct priority (Price Activation + Recipe Builder)
2. Adjust Phase 2-4 order if needed
3. Add/remove items based on business needs

---

## 6. User Experience Flows

### Critical User Journeys to Define

#### 6.1 Template Creation Flow
**Steps:**
1. Admin uploads PDF template
2. OCR auto-detects fields (dox-tmpl-pdf-recognizer)
3. Admin reviews/adjusts fields in Field Mapper
4. Admin saves template
5. (Optional) Admin adds template to Recipe

**Questions:**
- Should OCR run automatically on upload or manually triggered?
- Can admin skip OCR and place fields manually?
- How to handle OCR confidence < 0.7? (flag for manual review?)
- Should template save be immediate or require approval?

**UI Flow:**
- Upload screen → OCR results screen → Field Mapper → Save confirmation
- OR: Single-page wizard with steps?

---

#### 6.2 Contract Generation Flow
**Steps:**
1. User selects account (Account Hierarchy?)
2. User selects template recipe (Recipe Builder)
3. User fills in form fields (auto-populated from account?)
4. User previews generated contract
5. User sends for signature (AssureSign/DocuSeal)
6. User triggers price activation

**Questions:**
- Should contract generation be wizard-based or multi-page?
- How much data auto-populates from account? (all fields or subset?)
- Preview: Full PDF render or just field summary?
- Price activation: Automatic after signature or manual trigger?

**UI Flow:**
- Account selection → Recipe selection → Field entry → Preview → Send → Price activation

---

#### 6.3 Price Activation Flow
**Steps:**
1. Contract signed (webhook from e-signature service)
2. Pricing data extracted from contract
3. Submission created in Price Activation service
4. Submission sent to external pricing system
5. Status tracked (pending → processing → approved/rejected)
6. Retry if failed (up to 3 attempts)
7. Notification sent on final status

**Questions:**
- Who gets notified on failure? (submitter, admin, both?)
- Can user manually retry before max attempts?
- Should there be a "cancel submission" option?
- What happens to contract if pricing rejected? (flag account, block future contracts?)

**UI Flow:**
- Automatic trigger → Background processing → User views status dashboard → Manual retry if needed

---

#### 6.4 Tier Elevation Flow
**Steps:**
1. Quarterly job checks eligibility (dbo.Accounts data)
2. Auto-eligible accounts flagged for elevation
3. Admin reviews auto-eligible list
4. Admin approves elevation (or system auto-approves if configured)
5. Tier updated in database
6. User notified of new tier

**Questions:**
- Should elevation be fully automatic or require admin approval?
- Can users request manual elevation if not auto-eligible?
- What's the approval workflow for manual requests? (single approver, manager chain?)
- Demotion: Automatic or manual process?

**UI Flow:**
- Scheduled job → Admin dashboard shows eligible accounts → Admin approves → System updates tier → Notification sent

---

#### 6.5 Bulk Data Entry Flow (PasteBlox)
**Steps:**
1. User copies data from Excel/CSV
2. User pastes into PasteBlox textarea
3. Real-time validation runs (field types, required fields)
4. Errors displayed in error panel
5. User fixes errors (click error to jump to row)
6. User submits bulk data
7. Backend processes and saves to database
8. Success/failure summary shown

**Questions:**
- Max rows to support? (100, 1000, 10000?)
- Should user be able to save draft and come back later?
- Validation: Client-side only or backend validation too?
- What happens on partial failure? (rollback all or commit successful rows?)

**UI Flow:**
- Paste → Validate → Fix errors → Submit → Results

---

### Decision Point
**User should confirm:** Are these the right user journeys? Any missing?

---

## 7. Next Steps & Action Items

### Immediate Decisions Needed (This Session)
1. ✅ Technology stack: React, Vanilla JS, or Hybrid?
2. ✅ Integration architecture: iframe, Microfrontend, Full Page, or SPA?
3. ✅ Phase 1 priority confirmed: Price Activation + Recipe Builder?
4. ✅ Bridge.DOC Tools: Which 9 to evaluate first?

### Next Session Actions
1. Begin Phase 1 implementation (if stack decided)
2. Evaluate selected Bridge.DOC Tools (if user wants to see them first)
3. Define API contracts for Price Activation service
4. Design database schema for Recipe Builder

### Documentation to Create
1. API specification for dox-price-activation-service
2. Database schema for Phase 1 features
3. User journey wireframes (5 flows)
4. Component library structure (if React chosen)

---

## Summary

This session prepared:
- ✅ 4 new preview components (Field Mapper, Price Activation, Account Hierarchy, Tier Elevation)
- ✅ Organized session files in dox-admin/sessions/compyle-pact-implementation-plan-5/
- ✅ Identified 13 Bridge.DOC Tools (4 previewed, 9 to evaluate)
- ✅ Confirmed hybrid interface architecture (centralized + service-specific)

**Next session focus:** Interface discussion covering:
- Technology stack decision
- Integration architecture
- Implementation priorities
- Bridge.DOC Tools evaluation
- User experience flows

**User is ready to:** Run preview environment, review components, make decisions on implementation strategy.

---

**Prepared by:** Implementation Agent
**Date:** 2025-11-09
**Session:** compyle-pact-implementation-plan-5
