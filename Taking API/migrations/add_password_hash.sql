-- Migration: add password_hash column to users
-- Run this against your Postgres database (psql or any client):
-- ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;

ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;
