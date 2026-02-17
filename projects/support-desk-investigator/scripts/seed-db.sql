-- ============================================================================
-- Frappe Helpdesk Database Seed Script
-- ============================================================================
-- This script seeds the Frappe database with initial configuration and test data
-- Sections:
--   1. Webhooks - HD Ticket event webhooks
--   2. TODO: Customers - Demo customer data
--   3. TODO: Tickets - Sample support tickets
--   4. TODO: KB Articles - Knowledge base entries
-- ============================================================================

-- ============================================================================
-- SECTION 1: Webhooks
-- ============================================================================
-- Create webhooks for HD Ticket events to notify the backend service

-- Insert HD Ticket Creation Webhook
INSERT INTO `tabWebhook` (
    `name`,
    `creation`,
    `modified`,
    `modified_by`,
    `owner`,
    `docstatus`,
    `idx`,
    `webhook_doctype`,
    `webhook_docevent`,
    `enabled`,
    `request_url`,
    `is_dynamic_url`,
    `timeout`,
    `request_method`,
    `request_structure`,
    `enable_security`
) VALUES (
    'HD Ticket - Creation',
    NOW(),
    NOW(),
    'Administrator',
    'Administrator',
    0,
    0,
    'HD Ticket',
    'after_insert',
    1,
    'http://backend:8000/webhooks/frappe',
    0,
    5,
    'POST',
    '',
    0
);

-- Insert HD Ticket Update Webhook
INSERT INTO `tabWebhook` (
    `name`,
    `creation`,
    `modified`,
    `modified_by`,
    `owner`,
    `docstatus`,
    `idx`,
    `webhook_doctype`,
    `webhook_docevent`,
    `enabled`,
    `request_url`,
    `is_dynamic_url`,
    `timeout`,
    `request_method`,
    `request_structure`,
    `enable_security`
) VALUES (
    'HD Ticket - Update',
    NOW(),
    NOW(),
    'Administrator',
    'Administrator',
    0,
    0,
    'HD Ticket',
    'on_update',
    1,
    'http://backend:8000/webhooks/frappe',
    0,
    5,
    'POST',
    '',
    0
);

-- Insert Webhook Data fields for Creation webhook
INSERT INTO `tabWebhook Data` (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `fieldname`, `key`, `parent`, `parentfield`, `parenttype`) VALUES
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'name', 'name', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'subject', 'subject', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'description', 'description', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'status', 'status', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'priority', 'priority', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'contact', 'contact', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 7, 'customer', 'customer', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 8, 'creation', 'creation', 'HD Ticket - Creation', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 9, 'modified', 'modified', 'HD Ticket - Creation', 'webhook_data', 'Webhook');

-- Insert Webhook Data fields for Update webhook
INSERT INTO `tabWebhook Data` (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `fieldname`, `key`, `parent`, `parentfield`, `parenttype`) VALUES
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'name', 'name', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'subject', 'subject', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'description', 'description', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'status', 'status', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'priority', 'priority', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'contact', 'contact', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 7, 'customer', 'customer', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 8, 'creation', 'creation', 'HD Ticket - Update', 'webhook_data', 'Webhook'),
    (SUBSTRING(MD5(RAND()), 1, 10), NOW(), NOW(), 'Administrator', 'Administrator', 0, 9, 'modified', 'modified', 'HD Ticket - Update', 'webhook_data', 'Webhook');
