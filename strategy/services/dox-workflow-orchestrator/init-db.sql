-- Initialize database for DOX Workflow Orchestrator
-- Run this script when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create workflow states table (if not exists)
CREATE TABLE IF NOT EXISTS workflow_states (
    workflow_id VARCHAR(255) PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    current_state VARCHAR(50) NOT NULL,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create workflow step results table
CREATE TABLE IF NOT EXISTS workflow_step_results (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
    step_name VARCHAR(255) NOT NULL,
    step_action VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    result JSONB,
    error_message TEXT,
    duration_ms INTEGER,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create workflow events table
CREATE TABLE IF NOT EXISTS workflow_events (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflow_states(workflow_id),
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_states_status ON workflow_states(current_state);
CREATE INDEX IF NOT EXISTS idx_workflow_states_updated ON workflow_states(updated_at);
CREATE INDEX IF NOT EXISTS idx_workflow_states_service ON workflow_states(service);
CREATE INDEX IF NOT EXISTS idx_step_results_workflow ON workflow_step_results(workflow_id);
CREATE INDEX IF NOT EXISTS idx_step_results_executed ON workflow_step_results(executed_at);
CREATE INDEX IF NOT EXISTS idx_events_workflow ON workflow_events(workflow_id);
CREATE INDEX IF NOT EXISTS idx_events_published ON workflow_events(published_at);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dox_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dox_user;