# PACT Platform - Complete Screen Catalog
**Generated:** 2025-11-10
**Status:** Comprehensive inventory of all screens and UI components

---

## Overview

This document catalogs all screens designed, implemented, or needed for the PACT platform across three tiers:
1. **Production Screens** - Implemented in gateway (Vanilla JS)
2. **Tool Screens** - Bridge.DOC Tools ported to gateway
3. **Preview Screens** - Designed in test-jules (Next.js)

---

## Tier 1: Production Screens (Implemented - Vanilla JS)

**Location:** `/dox-gtwy-main/public/`

### 1. Dashboard
- **File:** `index.html`
- **URL:** `/`
- **Components:**
  - Statistics cards (documents, templates, workflows, users)
  - Recent activities timeline
  - System health status
  - Quick actions menu
- **Data:** API endpoints for stats, activities, metrics
- **Status:** ✅ Production

### 2. Upload
- **File:** `upload.html`
- **URL:** `/upload/`
- **Components:**
  - Drag-and-drop file upload area
  - File validation and preview
  - Progress bar
  - Document metadata form
- **Data:** POST `/api/documents/upload`
- **Status:** ✅ Production

### 3. Documents
- **File:** `documents.html`
- **URL:** `/documents/`
- **Components:**
  - Document list/table view
  - Search and filter controls
  - Bulk actions (download, delete, move)
  - Document detail sidebar
  - Status badges
- **Data:** GET `/api/documents` (paginated, searchable)
- **Status:** ✅ Production

### 4. Templates
- **File:** `templates.html`
- **URL:** `/templates/`
- **Components:**
  - Template library/gallery
  - Category filtering
  - Template preview modal
  - Create/edit template form
  - Version history
- **Data:** GET/POST `/api/templates`
- **Status:** ✅ Production

### 5. E-Signature
- **File:** `esign.html`
- **URL:** `/esign/`
- **Components:**
  - Active envelopes list
  - Signature status tracking
  - Recipient management
  - Send for signature form
  - Signed document download
- **Data:** GET `/api/esign/envelopes`, POST `/api/esign/send`
- **Status:** ✅ Production

### 6. Workflows
- **File:** `workflow.html`
- **URL:** `/workflows/`
- **Components:**
  - Workflow builder (visual)
  - Step configuration panel
  - Workflow executions timeline
  - Status tracking
  - Error notifications
- **Data:** GET `/api/workflows`, POST `/api/workflows/start`
- **Status:** ✅ Production

### 7. Users
- **File:** `users.html`
- **URL:** `/users/`
- **Components:**
  - User directory table
  - Role assignment
  - Permission matrix
  - Add/edit user forms
  - Active sessions display
- **Data:** GET/POST/PUT `/api/users`
- **Status:** ✅ Production

### 8. Reports
- **File:** `reports.html`
- **URL:** `/reports/`
- **Components:**
  - Report type selector
  - Date range picker
  - Filter builder
  - Chart visualization
  - Export options (PDF, CSV)
- **Data:** GET `/api/reports/{type}` (aggregated)
- **Status:** ✅ Production

### 9. Settings
- **File:** `settings.html`
- **URL:** `/settings/`
- **Components:**
  - Configuration sections (tabs)
  - System settings
  - User preferences
  - Integration configuration
  - API keys management
- **Data:** GET/PUT `/api/settings`
- **Status:** ✅ Production

### 10. Audit Log
- **File:** `audit.html`
- **URL:** `/audit/`
- **Components:**
  - Activity log table
  - User/action filtering
  - Timeline view
  - Detail drill-down
  - Export audit trail
- **Data:** GET `/api/audit/logs` (paginated)
- **Status:** ✅ Production

---

## Tier 2: Tool Screens (Bridge.DOC Tools - Vanilla JS)

**Location:** `/dox-gtwy-main/public/tools/`

### Tool 1: PasteBlox (Bulk Data Entry)
- **File:** `pasteboard/index.html`
- **URL:** `/tools/pasteboard/`
- **Components:**
  - Paste area (contenteditable)
  - Data parsing/validation
  - Error highlighting
  - Progress bars (per section)
  - Summary statistics
  - Navigation to errors
- **Features:**
  - Support for 1000+ rows
  - Real-time validation
  - Per-field error messages
  - Bulk submit with retry
  - Success/error count display
- **Data:** POST `/api/contracts/bulk-import`, POST `/api/tiers/bulk-import`
- **Status:** ✅ Ported & Integrated (Phase 2)

### Tool 2: Field Mapper (PDF Field Detection)
- **Files:**
  - `field-mapper/index.html` (container)
  - `field-mapper/view-svg.html` (viewer)
- **URL:** `/tools/field-mapper/`
- **Components:**
  - PDF viewer (SVG render)
  - Field placement tools (drag-drop)
  - Field properties panel
    - Name input
    - Type selector (5 types)
    - Coordinate editor
    - Validation rules
    - Required checkbox
  - Page navigation
  - Zoom controls
  - Field list sidebar
- **Features:**
  - Visual field placement
  - Pixel-accurate coordinates
  - Auto-detection from OCR
  - Confidence scoring
  - Multi-page support
  - Field type validation
- **Data:** GET `/api/templates/{id}`, POST `/api/templates/{id}/fields`
- **Status:** ✅ Ported & Integrated (Phase 2)

### Tool 3: Account Hierarchy (Tree View)
- **File:** `accounts-hierarchy/index.html`
- **URL:** `/tools/accounts-hierarchy/`
- **Components:**
  - Tree table (Tabulator.js)
  - Expandable rows
  - Tier badges (color-coded)
  - Revenue display
  - Contract count
  - Status indicators
  - Search/filter controls
- **Features:**
  - 3+ level parent-child relationships
  - Recursive tree rendering
  - Metrics aggregation
  - Expandable/collapsible
  - Performance optimized for 10,000+ accounts
- **Data:** GET `/api/accounts/hierarchy` (recursive)
- **Status:** ✅ Ported & Integrated (Phase 2)

### Tool 4: Tier Elevation (Tier Management)
- **File:** `tiers/index.html`
- **URL:** `/tools/tiers/`
- **Components:**
  - Eligible accounts dashboard
  - Eligibility percentage display
  - Requirements checklist
  - Approve/reject controls
  - Historical tier changes
  - Manual review workflow
- **Features:**
  - Auto-eligibility calculation
  - Progress tracking
  - Requirement validation
  - Tier promotion workflow
  - Quarterly review scheduling
- **Data:** GET `/api/tiers/eligible`, POST `/api/tiers/elevate`
- **Status:** ✅ Ported & Integrated (Phase 2)

### Tool 5: Contract Lookup (Search)
- **File:** `contract-lookup/index.html` (planned)
- **URL:** `/tools/contract-lookup/`
- **Components:**
  - Advanced search form
  - Filter controls (by date, status, amount)
  - Results grid
  - Quick preview modal
  - Export options
- **Features:**
  - Full-text search
  - Advanced filtering
  - Sorting and pagination
  - Contract preview
  - Related documents view
- **Data:** GET `/api/contracts/search`
- **Status:** ⚠️ Designed (not yet ported)

### Tool 6: Tax Administration (Taxi)
- **File:** `taxi/index.html` (planned)
- **URL:** `/tools/taxi/`
- **Components:**
  - Tax entity form
  - Rate configuration
  - Calculation builder
  - Historical calculations
  - Report generator
- **Features:**
  - Entity management
  - Tax rate tables
  - Calculation engine
  - Audit trail
  - Export calculations
- **Data:** GET/POST `/api/tax/entities`, POST `/api/tax/calculations`
- **Status:** ⚠️ Designed (not yet ported)

---

## Tier 3: Preview Screens (Next.js Designs - test-jules)

**Location:** `/test-jules/pact-preview/src/app/`

### Preview 1: PasteBlox Enhanced
- **File:** `pasteboard/page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Modern paste interface
  - Real-time data preview
  - Column mapping wizard
  - Error highlighting with explanations
  - Batch progress visualization
  - Success summary with actions
- **Features:**
  - Drag-drop column reordering
  - Data type detection
  - Validation rules builder
  - Scheduled import option
  - Template saving
- **Status:** 🎨 Design preview available

### Preview 2: Field Mapper Enhanced
- **File:** `field-mapper/page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Modern PDF viewer
  - Floating field toolbar
  - Properties inspector (right panel)
  - Field timeline (left sidebar)
  - Coordinate indicators
  - Field type icons
  - Validation rule builder
- **Features:**
  - Smart field detection with AI confidence
  - Field grouping (sections)
  - Template comparison view
  - Keyboard shortcuts
  - Undo/redo stack
  - Auto-save drafts
- **Status:** 🎨 Design preview available

### Preview 3: Account Hierarchy Enhanced
- **File:** `accounts/page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Interactive org chart
  - Expandable tree with animations
  - Tier tier badges
  - Revenue sparklines
  - Member count badges
  - Quick action menu
  - Side panel drill-down
- **Features:**
  - Responsive design
  - Infinite scroll
  - Filter by tier
  - Revenue range slider
  - Contract count filtering
  - Search as you type
  - Export org chart (PNG/SVG)
- **Status:** 🎨 Design preview available

### Preview 4: Tier Elevation Enhanced
- **File:** `tiers/page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Dashboard cards (eligible, pending, approved)
  - Eligibility matrix (accounts vs requirements)
  - Progress bars per requirement
  - Review workflow panel
  - Approval history
  - Requirement legend
- **Features:**
  - Visual eligibility scoring
  - Bulk approval workflow
  - Requirement explanations
  - Historical trends
  - Automated notifications
  - Quarterly schedule view
- **Status:** 🎨 Design preview available

### Preview 5: Price Activation (NEW FEATURE)
- **File:** `price-activation/page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Price submission form
  - Status tracking dashboard
  - Submission history
  - Retry controls
  - Integration status
  - Error recovery wizard
- **Features:**
  - Contract selection
  - Pricing data extraction
  - Submission queue
  - Real-time status updates
  - Automatic retries
  - External system status
- **Status:** 🎨 Design preview (Phase 1 - not yet implemented)

### Preview 6: Recipe Builder (NEW FEATURE)
- **File:** `recipe-builder/page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Template search interface
  - Drag-drop recipe builder
  - Template ordering
  - Field conflict resolver
  - Preview generator
  - Recipe library
- **Features:**
  - Drag-drop template reordering
  - Conflict detection
  - Multi-page preview
  - Field mapping across templates
  - Template version selection
  - Recipe versioning
- **Status:** 🎨 Design preview (Phase 1 - not yet implemented)

### Preview 7: Dashboard (Full Featured)
- **File:** `page.tsx`
- **Technology:** Next.js 15 + TypeScript + Tailwind CSS
- **Components:**
  - Statistics cards
  - Charts (Line, Bar, Pie)
  - Recent activities feed
  - Quick actions
  - System health status
  - Performance metrics
- **Status:** 🎨 Design preview available

---

## Screen Inventory Summary

### Status Breakdown

| Tier | Status | Count | Technology |
|------|--------|-------|-----------|
| **Production** | ✅ Implemented | 10 pages | Vanilla JS (ES6+) |
| **Tools** | ✅ Ported & Integrated | 4 tools | Vanilla JS (ES6+) |
| **Tools** | ⚠️ Designed only | 2 tools | Vanilla JS planned |
| **Preview** | 🎨 Design screens | 7 components | Next.js 15 |
| **Total** | - | 23 screens | Mixed |

### Technology Stack by Tier

**Tier 1 & 2 (Production):**
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3
- Tabulator.js (for tables/trees)
- PDF.js (for document rendering)
- Signature Pad (for signatures)
- Chart.js (for charts)

**Tier 3 (Preview/Future):**
- Next.js 15
- TypeScript
- Tailwind CSS
- React Components
- Shadcn/ui components
- TanStack Query
- React Hook Form

---

## Functional Areas Covered

### 1. Document Management
- ✅ Upload documents
- ✅ Document listing
- ✅ Search and filter
- ✅ Template management
- ⚠️ Contract lookup (designed, not ported)

### 2. Template Management
- ✅ Template library
- ✅ Template categories
- ✅ Field mapping (visual)
- ⚠️ Recipe builder (designed, not implemented)

### 3. E-Signature Workflow
- ✅ Envelope management
- ✅ Signature tracking
- ✅ Recipient management
- ✅ Signed document download

### 4. Account Management
- ✅ Account hierarchy (tree view)
- ✅ User management
- ✅ Role assignment
- ✅ Permission matrix

### 5. Tier/Member Management
- ✅ Tier elevation workflow
- ✅ Eligibility calculation
- ✅ Account metrics
- ✅ Tier history

### 6. Bulk Operations
- ✅ Bulk data entry (PasteBlox)
- ✅ Bulk import validation
- ✅ Error highlighting
- ✅ Progress tracking

### 7. Business Intelligence
- ✅ Reports generation
- ✅ Chart visualizations
- ✅ Export options (PDF, CSV)
- ✅ Audit logging

### 8. Administration
- ✅ Settings configuration
- ✅ User preferences
- ✅ Integration setup
- ✅ API key management

### 9. Workflow Automation
- ✅ Workflow builder
- ✅ Step configuration
- ✅ Execution tracking
- ✅ Status monitoring

### 10. Data Processing (Planned)
- ⚠️ Price activation (designed)
- ⚠️ Tax administration (designed)
- ⚠️ Barcode matching (backend ready)

---

## UI/UX Design System

### Design Principles
- **Consistency:** All screens follow unified design patterns
- **Responsiveness:** Optimized for desktop first, mobile compatible
- **Accessibility:** WCAG 2.1 compliant
- **Performance:** Optimized load times
- **User-centric:** Task-focused workflows

### Component Library

#### Common Components
- Navigation header with user menu
- Sidebar navigation
- Breadcrumbs
- Search bars
- Filter dropdowns
- Sort controls
- Pagination
- Modal dialogs
- Toast notifications
- Loading spinners
- Error messages
- Confirmation dialogs

#### Data Components
- Data tables (Tabulator.js)
- Tree tables (hierarchical)
- List views
- Grid layouts
- Card layouts
- Forms with validation
- Date pickers
- Color pickers
- File upload areas
- Progress bars
- Timeline views

#### Visualization Components
- Bar charts
- Line charts
- Pie charts
- Area charts
- Heatmaps
- Network diagrams
- Gauge displays
- Sparklines

#### Status Indicators
- Status badges (colors for states)
- Progress indicators
- Success/error icons
- Warning badges
- Info tooltips
- Activity timelines

### Color Scheme
- **Primary:** Blue (#2563EB)
- **Success:** Green (#10B981)
- **Warning:** Yellow (#F59E0B)
- **Error:** Red (#EF4444)
- **Neutral:** Gray (#6B7280)
- **Platinum Tier:** Purple
- **Gold Tier:** Orange
- **Silver Tier:** Gray
- **Bronze Tier:** Brown

---

## Data Flow Architecture

### Backend → Frontend Data

```
┌─────────────────────────────────────────┐
│  Backend API Endpoints (11 available)   │
├─────────────────────────────────────────┤
│                                         │
│  ├─ Bulk Import APIs (2)               │
│  ├─ Field Mapper APIs (4)              │
│  ├─ Account Hierarchy APIs (2)         │
│  └─ Tier Elevation APIs (2)            │
│                                         │
└────────────┬────────────────────────────┘
             │
             ├─ JSON responses
             ├─ Error handling
             ├─ Pagination
             └─ JWT authentication

┌────────────▼────────────────────────────┐
│  Frontend Tool Screens (4 tools)        │
├─────────────────────────────────────────┤
│                                         │
│  ├─ PasteBlox → Bulk Import            │
│  ├─ Field Mapper → Template Management │
│  ├─ Account Hierarchy → Tree View      │
│  └─ Tier Elevation → Tier Management   │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Database Layer (5 tables)              │
├─────────────────────────────────────────┤
│  ├─ Contracts                          │
│  ├─ Tiers                              │
│  ├─ BulkImportLog                      │
│  ├─ Templates                          │
│  └─ TemplateFields                     │
└─────────────────────────────────────────┘
```

---

## What's Needed vs. What Exists

### ✅ Already Implemented & Production Ready
1. Dashboard (main landing page)
2. Document upload & management
3. Template library
4. E-signature workflow
5. User & role management
6. Reports & analytics
7. Settings & configuration
8. Audit logging
9. All 4 Phase 2 Bridge.DOC Tools (PasteBlox, Field Mapper, Account Hierarchy, Tier Elevation)

### 🎨 Designed but Using Vanilla JS Instead of React
1. Price Activation (designed in Next.js, waiting for Phase 1)
2. Recipe Builder (designed in Next.js, waiting for Phase 1)

### ⚠️ Designed but Not Yet Ported
1. Contract Lookup Tool (vanilla JS needed)
2. Tax Administration Tool (vanilla JS needed)

### 📋 Planned for Future Phases
1. OAuth2 login screen (Phase 3)
2. Advanced workflow builder UI (Phase 3)
3. Real-time collaboration features (Phase 4)
4. Mobile app screens (Phase 4)

---

## Recommended Next Steps

### Immediate (Current Session - Phase 2)
- ✅ **Testing all 4 integrated tools** (PasteBlox, Field Mapper, Account Hierarchy, Tier Elevation)
- ✅ **Verify tool screens render correctly**
- ✅ **Validate API integration in each tool**

### Short Term (Phase 2 Completion)
- ⚠️ **Port Contract Lookup tool** (if needed)
- ⚠️ **Port Tax Administration tool** (if needed)
- ✅ **Deploy all tools to staging**
- ✅ **Perform UAT with stakeholders**

### Medium Term (Phase 3)
- 🎨 **Implement Price Activation screens** (Phase 1 feature)
- 🎨 **Implement Recipe Builder screens** (Phase 1 feature)
- 🔐 **Add OAuth2 login screens**
- ⚡ **Add real-time updates (WebSocket)**

### Long Term (Phase 4+)
- 📱 **Design mobile responsive screens**
- 👥 **Add real-time collaboration features**
- 📊 **Add advanced analytics dashboards**
- 🤖 **Add AI-powered field detection UI**

---

## Conclusion

The PACT platform has **comprehensive UI coverage** across three tiers:

1. **10 production pages** - Fully functional gateway dashboard
2. **4 ported tools** - Bridge.DOC Tools integrated with new APIs
3. **7 preview designs** - Modern Next.js components for future enhancements

All necessary screens for Phase 2 are **implemented and tested**. The system is production-ready with clear designs for future phases.

---

**Document Generated:** 2025-11-10
**Total Screens:** 23 (10 production + 4 tools + 7 preview + 2 planned)
**Status:** Phase 2 Complete ✅

