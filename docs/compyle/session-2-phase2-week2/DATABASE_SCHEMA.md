# dox-core-store Database Schema

## Overview

Multi-tenant database schema for the Pact Platform core data store. All tables include `siteId` for tenant isolation and follow standard naming conventions.

## Design Principles

1. **Multi-tenancy**: All tables include `siteId` for tenant isolation
2. **Audit Trail**: All tables include `createdBy`, `createdAt`, `updatedBy`, `updatedAt`
3. **Soft Deletes**: Critical tables include `deletedAt` for soft deletion
4. **Performance**: Proper indexing and foreign key relationships
5. **Normalization**: Third normal form where appropriate

## Core Tables

### 1. Sites (Tenants)
```sql
CREATE TABLE sites (
    siteId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    siteName NVARCHAR(100) NOT NULL,
    siteDescription NVARCHAR(500),
    siteDomain NVARCHAR(255),
    isActive BIT DEFAULT 1,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),
    updatedBy UNIQUEIDENTIFIER,
    updatedAt DATETIME2,
    deletedAt DATETIME2 NULL
);

CREATE INDEX idx_sites_siteName ON sites(siteName);
CREATE INDEX idx_sites_domain ON sites(siteDomain);
CREATE INDEX idx_sites_active ON sites(isActive);
```

### 2. Users
```sql
CREATE TABLE users (
    userId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    siteId UNIQUEIDENTIFIER NOT NULL,
    userPrincipalName NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    firstName NVARCHAR(100),
    lastName NVARCHAR(100),
    isActive BIT DEFAULT 1,
    lastLoginAt DATETIME2,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),
    updatedBy UNIQUEIDENTIFIER,
    updatedAt DATETIME2,
    deletedAt DATETIME2 NULL,

    CONSTRAINT fk_users_site FOREIGN KEY (siteId) REFERENCES sites(siteId),
    CONSTRAINT uk_users_upn_site UNIQUE (userPrincipalName, siteId),
    CONSTRAINT uk_users_email_site UNIQUE (email, siteId)
);

CREATE INDEX idx_users_siteId ON users(siteId);
CREATE INDEX idx_users_upn ON users(userPrincipalName);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(isActive);
CREATE INDEX idx_users_lastLogin ON users(lastLoginAt);
```

### 3. Documents
```sql
CREATE TABLE documents (
    documentId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    siteId UNIQUEIDENTIFIER NOT NULL,
    documentName NVARCHAR(255) NOT NULL,
    documentDescription NVARCHAR(1000),
    documentType NVARCHAR(50) NOT NULL, -- 'PDF', 'DOCX', 'XLSX', etc.
    mimeType NVARCHAR(100) NOT NULL,
    fileSizeBytes BIGINT NOT NULL,
    sharePointId NVARCHAR(255), -- SharePoint file ID
    sharePointPath NVARCHAR(500),
    sharePointUrl NVARCHAR(1000),
    version INT DEFAULT 1,
    isActive BIT DEFAULT 1,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),
    updatedBy UNIQUEIDENTIFIER,
    updatedAt DATETIME2,
    deletedAt DATETIME2 NULL,

    CONSTRAINT fk_documents_site FOREIGN KEY (siteId) REFERENCES sites(siteId),
    CONSTRAINT fk_documents_user FOREIGN KEY (createdBy) REFERENCES users(userId)
);

CREATE INDEX idx_documents_siteId ON documents(siteId);
CREATE INDEX idx_documents_name ON documents(documentName);
CREATE INDEX idx_documents_type ON documents(documentType);
CREATE INDEX idx_documents_sharepoint ON documents(sharePointId);
CREATE INDEX idx_documents_created ON documents(createdAt);
CREATE INDEX idx_documents_active ON documents(isActive);
```

### 4. Templates
```sql
CREATE TABLE templates (
    templateId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    siteId UNIQUEIDENTIFIER NOT NULL,
    templateName NVARCHAR(255) NOT NULL,
    templateDescription NVARCHAR(1000),
    documentId UNIQUEIDENTIFIER NOT NULL, -- Reference to the base document
    templateType NVARCHAR(50) NOT NULL, -- 'ASSURESIGN', 'INTERNAL', 'EXTERNAL'
    isActive BIT DEFAULT 1,
    version INT DEFAULT 1,
    isPublished BIT DEFAULT 0,
    publishedBy UNIQUEIDENTIFIER,
    publishedAt DATETIME2,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),
    updatedBy UNIQUEIDENTIFIER,
    updatedAt DATETIME2,
    deletedAt DATETIME2 NULL,

    CONSTRAINT fk_templates_site FOREIGN KEY (siteId) REFERENCES sites(siteId),
    CONSTRAINT fk_templates_document FOREIGN KEY (documentId) REFERENCES documents(documentId),
    CONSTRAINT fk_templates_user FOREIGN KEY (createdBy) REFERENCES users(userId),
    CONSTRAINT fk_templates_published FOREIGN KEY (publishedBy) REFERENCES users(userId),
    CONSTRAINT uk_templates_name_site UNIQUE (templateName, siteId)
);

CREATE INDEX idx_templates_siteId ON templates(siteId);
CREATE INDEX idx_templates_name ON templates(templateName);
CREATE INDEX idx_templates_type ON templates(templateType);
CREATE INDEX idx_templates_document ON templates(documentId);
CREATE INDEX idx_templates_published ON templates(isPublished);
CREATE INDEX idx_templates_active ON templates(isActive);
```

### 5. Template Fields
```sql
CREATE TABLE templateFields (
    fieldId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    templateId UNIQUEIDENTIFIER NOT NULL,
    fieldName NVARCHAR(100) NOT NULL,
    fieldType NVARCHAR(50) NOT NULL, -- 'TEXT', 'NUMBER', 'DATE', 'SIGNATURE', 'CHECKBOX'
    fieldLabel NVARCHAR(255),
    pageIndex INT NOT NULL,
    xCoordinate DECIMAL(10,2) NOT NULL,
    yCoordinate DECIMAL(10,2) NOT NULL,
    width DECIMAL(10,2) NOT NULL,
    height DECIMAL(10,2) NOT NULL,
    isRequired BIT DEFAULT 0,
    defaultValue NVARCHAR(500),
    validationRules NVARCHAR(1000), -- JSON string of validation rules
    sortOrder INT DEFAULT 0,
    isActive BIT DEFAULT 1,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),
    updatedBy UNIQUEIDENTIFIER,
    updatedAt DATETIME2,

    CONSTRAINT fk_templateFields_template FOREIGN KEY (templateId) REFERENCES templates(templateId),
    CONSTRAINT fk_templateFields_user FOREIGN KEY (createdBy) REFERENCES users(userId),
    CONSTRAINT uk_templateFields_name_template UNIQUE (fieldName, templateId)
);

CREATE INDEX idx_templateFields_templateId ON templateFields(templateId);
CREATE INDEX idx_templateFields_name ON templateFields(fieldName);
CREATE INDEX idx_templateFields_type ON templateFields(fieldType);
CREATE INDEX idx_templateFields_position ON templateFields(pageIndex, xCoordinate, yCoordinate);
CREATE INDEX idx_templateFields_sort ON templateFields(sortOrder);
```

### 6. Bundles
```sql
CREATE TABLE bundles (
    bundleId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    siteId UNIQUEIDENTIFIER NOT NULL,
    bundleName NVARCHAR(255) NOT NULL,
    bundleDescription NVARCHAR(1000),
    isActive BIT DEFAULT 1,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),
    updatedBy UNIQUEIDENTIFIER,
    updatedAt DATETIME2,
    deletedAt DATETIME2 NULL,

    CONSTRAINT fk_bundles_site FOREIGN KEY (siteId) REFERENCES sites(siteId),
    CONSTRAINT fk_bundles_user FOREIGN KEY (createdBy) REFERENCES users(userId),
    CONSTRAINT uk_bundles_name_site UNIQUE (bundleName, siteId)
);

CREATE INDEX idx_bundles_siteId ON bundles(siteId);
CREATE INDEX idx_bundles_name ON bundles(bundleName);
CREATE INDEX idx_bundles_active ON bundles(isActive);
```

### 7. Bundle Templates (Junction Table)
```sql
CREATE TABLE bundleTemplates (
    bundleTemplateId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    bundleId UNIQUEIDENTIFIER NOT NULL,
    templateId UNIQUEIDENTIFIER NOT NULL,
    sortOrder INT DEFAULT 0,
    isRequired BIT DEFAULT 1,
    createdBy UNIQUEIDENTIFIER NOT NULL,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),

    CONSTRAINT fk_bundleTemplates_bundle FOREIGN KEY (bundleId) REFERENCES bundles(bundleId) ON DELETE CASCADE,
    CONSTRAINT fk_bundleTemplates_template FOREIGN KEY (templateId) REFERENCES templates(templateId) ON DELETE CASCADE,
    CONSTRAINT fk_bundleTemplates_user FOREIGN KEY (createdBy) REFERENCES users(userId),
    CONSTRAINT uk_bundleTemplates_bundle_template UNIQUE (bundleId, templateId)
);

CREATE INDEX idx_bundleTemplates_bundleId ON bundleTemplates(bundleId);
CREATE INDEX idx_bundleTemplates_templateId ON bundleTemplates(templateId);
CREATE INDEX idx_bundleTemplates_sort ON bundleTemplates(bundleId, sortOrder);
```

## Supporting Tables

### 8. Document Storage
```sql
CREATE TABLE documentStorage (
    storageId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    siteId UNIQUEIDENTIFIER NOT NULL,
    documentId UNIQUEIDENTIFIER NOT NULL,
    storageType NVARCHAR(50) NOT NULL, -- 'SHAREPOINT', 'LOCAL', 'BLOB'
    storagePath NVARCHAR(1000) NOT NULL,
    storageUrl NVARCHAR(1000),
    storageMetadata NVARCHAR(MAX), -- JSON metadata
    isPrimary BIT DEFAULT 1,
    createdAt DATETIME2 DEFAULT GETUTCDATE(),

    CONSTRAINT fk_documentStorage_site FOREIGN KEY (siteId) REFERENCES sites(siteId),
    CONSTRAINT fk_documentStorage_document FOREIGN KEY (documentId) REFERENCES documents(documentId),
    CONSTRAINT uk_documentStorage_document_primary UNIQUE (documentId, isPrimary) WHERE isPrimary = 1
);

CREATE INDEX idx_documentStorage_siteId ON documentStorage(siteId);
CREATE INDEX idx_documentStorage_documentId ON documentStorage(documentId);
CREATE INDEX idx_documentStorage_type ON documentStorage(storageType);
```

### 9. Audit Logs
```sql
CREATE TABLE auditLogs (
    logId BIGINT IDENTITY(1,1) PRIMARY KEY,
    siteId UNIQUEIDENTIFIER NOT NULL,
    userId UNIQUEIDENTIFIER,
    entityType NVARCHAR(100) NOT NULL,
    entityId UNIQUEIDENTIFIER NOT NULL,
    action NVARCHAR(50) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'DOWNLOAD'
    oldValues NVARCHAR(MAX), -- JSON of old values
    newValues NVARCHAR(MAX), -- JSON of new values
    ipAddress NVARCHAR(45),
    userAgent NVARCHAR(500),
    createdAt DATETIME2 DEFAULT GETUTCDATE(),

    CONSTRAINT fk_auditLogs_site FOREIGN KEY (siteId) REFERENCES sites(siteId),
    CONSTRAINT fk_auditLogs_user FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE INDEX idx_auditLogs_siteId ON auditLogs(siteId);
CREATE INDEX idx_auditLogs_userId ON auditLogs(userId);
CREATE INDEX idx_auditLogs_entity ON auditLogs(entityType, entityId);
CREATE INDEX idx_auditLogs_action ON auditLogs(action);
CREATE INDEX idx_auditLogs_created ON auditLogs(createdAt);
```

## Views

### 1. Active Templates View
```sql
CREATE VIEW vw_activeTemplates AS
SELECT
    t.templateId,
    t.siteId,
    t.templateName,
    t.templateDescription,
    t.templateType,
    t.version,
    d.documentName,
    d.documentType,
    d.mimeType,
    d.fileSizeBytes,
    u.firstName + ' ' + u.lastName AS createdByName,
    t.createdAt,
    t.publishedAt,
    (SELECT COUNT(*) FROM templateFields tf WHERE tf.templateId = t.templateId AND tf.isActive = 1) AS fieldCount
FROM templates t
INNER JOIN documents d ON t.documentId = d.documentId
INNER JOIN users u ON t.createdBy = u.userId
WHERE t.isActive = 1;
```

### 2. Bundle Details View
```sql
CREATE VIEW vw_bundleDetails AS
SELECT
    b.bundleId,
    b.siteId,
    b.bundleName,
    b.bundleDescription,
    u.firstName + ' ' + u.lastName AS createdByName,
    b.createdAt,
    (SELECT COUNT(*) FROM bundleTemplates bt WHERE bt.bundleId = b.bundleId) AS templateCount
FROM bundles b
INNER JOIN users u ON b.createdBy = u.userId
WHERE b.isActive = 1;
```

## Stored Procedures

### 1. Get Document with Storage
```sql
CREATE PROCEDURE sp_getDocumentWithStorage
    @siteId UNIQUEIDENTIFIER,
    @documentId UNIQUEIDENTIFIER
AS
BEGIN
    SELECT
        d.*,
        ds.storageType,
        ds.storagePath,
        ds.storageUrl,
        ds.storageMetadata
    FROM documents d
    LEFT JOIN documentStorage ds ON d.documentId = ds.documentId AND ds.isPrimary = 1
    WHERE d.siteId = @siteId
    AND d.documentId = @documentId
    AND d.isActive = 1;
END;
```

### 2. Create Template with Fields
```sql
CREATE PROCEDURE sp_createTemplateWithFields
    @siteId UNIQUEIDENTIFIER,
    @templateName NVARCHAR(255),
    @templateDescription NVARCHAR(1000),
    @documentId UNIQUEIDENTIFIER,
    @templateType NVARCHAR(50),
    @createdBy UNIQUEIDENTIFIER,
    @fields NVARCHAR(MAX) -- JSON array of fields
AS
BEGIN
    DECLARE @templateId UNIQUEIDENTIFIER = NEWID();

    BEGIN TRANSACTION;

    -- Create template
    INSERT INTO templates (templateId, siteId, templateName, templateDescription, documentId, templateType, createdBy)
    VALUES (@templateId, @siteId, @templateName, @templateDescription, @documentId, @templateType, @createdBy);

    -- Create fields from JSON
    -- Implementation depends on SQL Server version and JSON support

    COMMIT TRANSACTION;

    SELECT @templateId AS templateId;
END;
```

## Performance Optimizations

### Indexes
- All foreign key columns indexed
- Composite indexes for common query patterns
- Filtered indexes for active records

### Partitioning (Future)
- Consider partitioning large tables by `siteId`
- Archive old audit logs to separate tables

### Connection Pooling
- Application-level connection pooling
- Query timeout optimization

## Security Considerations

1. **Row-Level Security**: Implement RLS for multi-tenant isolation
2. **Data Encryption**: Encrypt sensitive columns at rest
3. **Audit Trail**: Complete audit logging for all operations
4. **Access Control**: Stored procedures for data access instead of direct table access

## Migration Strategy

1. **Alembic Migrations**: Version-controlled schema changes
2. **Backward Compatibility**: Support for multiple schema versions
3. **Data Validation**: Validate existing data during migrations
4. **Rollback Procedures**: Ability to rollback schema changes

---

**Last Updated**: 2025-11-02
**Schema Version**: 1.0
**Compatible with**: SQL Server 2019+