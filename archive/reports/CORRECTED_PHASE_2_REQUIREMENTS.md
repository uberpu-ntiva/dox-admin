# PACT Platform - Corrected Phase 2 Requirements
**Generated:** 2025-11-10
**Status:** Updated requirements based on user feedback
**Priority:** High - Critical corrections needed

---

## 🚨 **Critical Corrections to Phase 2 Requirements**

Based on your feedback, several key assumptions were incorrect. Here are the corrected requirements:

### ✅ **CORRECTED: Template Intake System**

**Current (Incorrect) Understanding:**
- Templates created via upload only
- Field Mapper creates template field definitions
- Manual template management

**CORRECTED Requirements:**
```
Template Intake Sources:
1. Upload via Upload Interface ✅
2. Intake from ACS.CONTRACTS → ACS.Attachments → acs.filehash tables
   - Filtering based on intelligence/simple matching
   - Automated template detection from existing contracts
3. Manual template creation (admin only)

Template Field Definitions:
- Field Mapper DEFINES QUERIES to get fields from CRM/others
- Field Mapper identifies field names for signer input
- Field Mapper identifies repeated use fields
- Field Mapper is ADMIN SCREEN for template managers
- NOT for end-user field placement on PDF
```

**Implementation Changes Needed:**
- Add ACS database integration for contract intake
- Change Field Mapper from PDF coordinate editor to query field mapping
- Field Mapper maps database fields → template fields
- Field Mapper is admin-only, not end-user facing
- Add intelligence filtering for contract-to-template detection

### ✅ **CORRECTED: Field Mapper Purpose**

**Current (Incorrect) Implementation:**
- Drag-drop field placement on PDF
- Coordinate editing (x, y, width, height)
- PDF visual field mapping

**CORRECTED Requirements:**
```
Field Mapper is ADMIN TOOL that:
1. Defines QUERIES to extract fields from external systems:
   - CRM fields
   - Database fields
   - API fields
   - Custom data sources

2. Maps external field names → template field names
3. Identifies fields that signers will fill out repeatedly
4. Creates field mapping rules for template generation

5. Does NOT place fields on PDF visually
6. Does NOT use coordinates (x, y, width, height)
7. Does NOT show PDF preview for field placement

8. Is for TEMPLATE MANAGERS only
```

**Implementation Changes Needed:**
- Remove PDF coordinate system from Field Mapper
- Replace with query builder interface
- Add external system connection setup
- Add field mapping configuration
- Add CRM/database field discovery
- Change from visual editor to admin configuration tool

### ✅ **CORRECTED: PasteBlox Context**

**Current (Incorrect) Understanding:**
- Generic bulk import tool for contracts and tiers
- General data entry interface

**CORRECTED Requirements:**
```
PasteBlox has VERY SPECIFIC USECASE:
- Port MUST follow DOX/.../Batch.aspx context exactly
- Preserves existing workflow and UI patterns
- Maintains compatibility with existing data structures
- Not a generic tool, but specific to Batch.aspx functionality

Implementation Approach:
- Port directly from DOX.Bridge.DOC/Tools/src/paste-board/
- Maintain exact same validation rules and data flow
- Preserve existing blokker/blox architecture
- Keep same column mapping and validation logic
```

**Implementation Changes Needed:**
- Review DOX/.../Batch.aspx for exact context
- Port existing validation logic exactly
- Maintain compatibility with current data structures
- Do not modernize - preserve existing patterns

### ✅ **CORRECTED: Account Hierarchy Scope**

**Current (Incorrect) Understanding:**
- Universal account management system
- Primary account interface

**CORRECTED Requirements:**
```
Account Hierarchy is LIMITED SCOPE:
- Only for certain account views
- May not be applicable beyond view/selection
- Specific to particular use cases
- Not a general account management interface

Implementation Changes Needed:
- Clarify specific use cases where hierarchy is needed
- May need to limit to certain contract types or workflows
- Focus on selection mechanism rather than full management
- May be conditional based on contract requirements
```

### ✅ **CORRECTED: Tier Elevation Requirements**

**Current (Incorrect) Implementation:**
- Simple eligibility dashboard
- Basic requirement checking
- Manual approval workflow

**CORRECTED Requirements:**
```
Tier Elevation Needs Rule Definition Expansion:
1. Rule definition interface for simple rules
2. Integration with financial reporting MCP bots
3. Complex eligibility criteria
4. Dynamic rule evaluation

Current spec is EXPANDING:
- Need more sophisticated rule engine
- Financial data integration
- Historical trend analysis
- Automated evaluation based on multiple criteria

Implementation Changes Needed:
- Expand from basic requirements to rule-based system
- Add MCP bot integration framework
- Design rule builder interface
- Add financial data import capabilities
- Implement rule evaluation engine
```

### ✅ **CORRECTED: Price Activation**

**Current (Incorrect) Design:**
- Contract pricing submission workflow
- External pricing system integration

**CORRECTED Requirements:**
```
Price Activation as OVERSIGHT MECHANISM:
1. Grid display with members by contract tier
2. Chargeback over time (z-index)
3. Historical system information from passthrough services
4. Grid-based view with marching pages
5. Oversight dashboard, not active submission

Key Features:
- Grid layout showing member tiers
- Time-based chargeback visualization
- System information aggregation
- Historical trend display
- Oversight and monitoring focus

Implementation Changes Needed:
- Change from submission workflow to oversight dashboard
- Implement grid-based data visualization
- Add time-series chargeback display
- Integrate with passthrough service data
- Focus on monitoring, not action
```

### ✅ **CORRECTED: Recipe Builder**

**Current (Incorrect) Understanding:**
- Interactive template bundling interface
- Drag-drop template selection

**CORRECTED Requirements:**
```
Recipe Builder is STORAGE MECHANISM:
1. Based on generated batches
2. Result of saving job as template
3. Simple storage interface
4. Can coordinate with template picker
5. NOT an interactive builder interface

Implementation Changes Needed:
- Simplify to storage interface
- Focus on batch-to-template conversion
- Remove complex builder interface
- Use with existing template picker
- Storage-focused rather than design-focused
```

---

## 🎯 **Data Picker Integration Requirement**

**New Universal Requirement:**
All interfaces for adding/managing groups of data should use the multi-mode data picker:

### Data Picker Modes (4 Themes)
1. **List Mode (Blue)** - Search-driven, two-stage selection
2. **Excel Mode (Green)** - Bulk import/export
3. **Form Mode (Purple)** - Individual item creation/editing
4. **Search Mode (Orange)** - Empty start, search & select

### Universal Integration Points
- Template selection interfaces
- Account selection in workflows
- Contract management
- User selection for notifications
- Document selection for operations
- Recipient selection in e-signature

**Implementation Priority:** High - This affects multiple screens

---

## 🔄 **Revised Implementation Plan**

### Phase 2 - Corrected Implementation

**Field Mapper (High Priority Changes):**
1. Remove PDF coordinate system
2. Implement query builder interface
3. Add CRM/database integration
4. Change to admin-only tool
5. Add field mapping configuration

**PasteBlox (High Priority Changes):**
1. Review DOX/.../Batch.aspx exact context
2. Port with existing patterns preserved
3. Maintain current validation and data flow
4. Do not modernize - preserve existing

**Tier Elevation (Medium Priority Changes):**
1. Expand to rule-based system
2. Add MCP bot integration
3. Implement rule builder interface
4. Add financial data integration

**Price Activation (High Priority Changes):**
1. Change to oversight dashboard
2. Implement grid-based visualization
3. Add time-series display
4. Integrate passthrough service data

**Recipe Builder (Low Priority Changes):**
1. Simplify to storage interface
2. Focus on batch-to-template conversion
3. Remove complex builder

**Account Hierarchy (Low Priority Changes):**
1. Clarify specific use cases
2. Focus on selection mechanism
3. May need to limit scope based on requirements

---

## 📋 **Data Picker Integration Plan**

### Universal Data Picker Components
- Mode selector (List/Excel/Form/Search)
- Tabulator datagrid integration
- Semantic theming system
- Collapsible sections with HTML5 details/summary
- Sticky bottom action area
- localStorage persistence
- Toast notifications

### Integration Points
Replace existing selection interfaces with data picker:
- Template selection (Templates page)
- Account selection (Multiple workflows)
- User selection (User management)
- Recipient selection (E-signature)
- Document selection (Bulk operations)

---

## 🚨 **Immediate Action Items**

### Priority 1: Critical Path Corrections
1. **Fix Field Mapper** - Change from visual to query-based
2. **Fix PasteBlox** - Port from exact Batch.aspx context
3. **Implement Data Picker** - Universal selection interface

### Priority 2: Scope Corrections
1. **Clarify Account Hierarchy** - Define specific use cases
2. **Expand Tier Elevation** - Add rule engine
3. **Redesign Price Activation** - Change to oversight dashboard

### Priority 3: Storage Corrections
1. **Simplify Recipe Builder** - Focus on storage mechanism
2. **Add Template Intake** - ACS database integration
3. **Integrate Financial Data** - MCP bot framework

---

## 📊 **Impact Assessment**

### High Impact Changes
- Field Mapper: Complete redesign needed
- PasteBlox: Context-specific port needed
- Price Activation: Different functionality entirely

### Medium Impact Changes
- Tier Elevation: Feature expansion
- Template Intake: New integration needed

### Low Impact Changes
- Account Hierarchy: Scope clarification
- Recipe Builder: Simplification

---

## 📚 **Reference Documents**

### Design Reference
- Figma Design: https://www.figma.com/make/0wGGQYkTt0OKzcNLSdxFdL/Data-Management-Interface
- Alternative: https://preview--tidy-checkboxes.lovable.app/

### Source Reference
- DOX/.../Batch.aspx (PasteBlox context)
- ACS database schema (template intake)
- Existing CRM/database integrations

---

**Status:** ✅ Requirements Corrected
**Next Action:** Implement corrected Field Mapper as admin query-based tool
**Priority:** High - Critical corrections needed for Phase 2 success