-- Run this script in the Supabase SQL editor to set up the database.

-- Main table: one row per SMS sent to a customer
CREATE TABLE IF NOT EXISTS feedback_requests (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token       UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),  -- unique link token sent in SMS
    customer_name   TEXT NOT NULL,
    phone_number    TEXT NOT NULL,
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    score           SMALLINT CHECK (score BETWEEN 1 AND 5),      -- filled when customer responds
    responded_at    TIMESTAMPTZ,
    google_sms_sent BOOLEAN NOT NULL DEFAULT FALSE,              -- TRUE if follow-up SMS with Google link was sent (score 4-5)
    email_notified  BOOLEAN NOT NULL DEFAULT FALSE               -- TRUE if manager email was sent (score 1-3)
);

-- Index for fast token lookups (used on the public feedback page)
CREATE INDEX IF NOT EXISTS idx_feedback_requests_token ON feedback_requests (token);

-- Index for dashboard queries sorted by date
CREATE INDEX IF NOT EXISTS idx_feedback_requests_sent_at ON feedback_requests (sent_at DESC);

-- Row Level Security: enable it, but allow full access to authenticated users (the manager)
ALTER TABLE feedback_requests ENABLE ROW LEVEL SECURITY;

-- Authenticated users (the manager, logged in via Supabase auth) can do everything.
-- The anon key + session token is used — no service role key needed.
CREATE POLICY "Authenticated users have full access"
    ON feedback_requests
    FOR ALL
    TO authenticated
    USING (TRUE)
    WITH CHECK (TRUE);

-- Anonymous users (customers opening the feedback link) can read any row.
-- Token filtering happens in application code via .eq("token", token).
CREATE POLICY "Anonymous can read by token"
    ON feedback_requests
    FOR SELECT
    TO anon
    USING (TRUE);

-- Anonymous users can submit score exactly once.
-- USING ensures the row's current score is NULL (prevents re-voting).
-- WITH CHECK ensures the new score is NOT NULL.
-- All fields (score, responded_at, google_sms_sent, email_notified) are set
-- in a single UPDATE call, so this policy fires only once per submission.
CREATE POLICY "Anonymous can submit score"
    ON feedback_requests
    FOR UPDATE
    TO anon
    USING (score IS NULL)
    WITH CHECK (score IS NOT NULL);
