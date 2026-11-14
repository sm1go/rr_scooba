-- Espoo Work Map — SQLite schema (spec section 2). Synthetic data only.
-- Bump `PRAGMA user_version` in app/api/db.py when this file changes.

PRAGMA user_version = 5;

CREATE TABLE user (
    id            TEXT PRIMARY KEY,
    email         TEXT UNIQUE,
    phone         TEXT,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('resident','employer','advisor')),
    name          TEXT NOT NULL DEFAULT '',
    employer_id   TEXT REFERENCES employer(id),
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE session (
    token      TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE resident_profile (
    user_id            TEXT PRIMARY KEY REFERENCES user(id) ON DELETE CASCADE,
    contact_method     TEXT CHECK (contact_method IN ('phone','sms','email')),
    district           TEXT,
    fields             TEXT NOT NULL DEFAULT '[]',
    availability       TEXT NOT NULL DEFAULT '[]',
    max_hours_per_week INTEGER,
    needs              TEXT NOT NULL DEFAULT '[]',
    languages          TEXT NOT NULL DEFAULT '[]',
    about              TEXT NOT NULL DEFAULT ''
);

CREATE TABLE employer (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    about         TEXT NOT NULL DEFAULT '',
    contact_name  TEXT NOT NULL DEFAULT '',
    contact_email TEXT NOT NULL DEFAULT '',
    contact_phone TEXT NOT NULL DEFAULT ''
);

CREATE TABLE event (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    date         TEXT NOT NULL,
    venue        TEXT NOT NULL DEFAULT '',
    advisor_note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE employer_event (
    employer_id TEXT NOT NULL REFERENCES employer(id),
    event_id    TEXT NOT NULL REFERENCES event(id),
    booth       TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (employer_id, event_id)
);

CREATE TABLE job (
    id              TEXT PRIMARY KEY,
    employer_id     TEXT NOT NULL REFERENCES employer(id),
    title           TEXT NOT NULL,
    field           TEXT NOT NULL DEFAULT '',
    duties          TEXT NOT NULL DEFAULT '[]',
    address         TEXT NOT NULL DEFAULT '',
    district        TEXT NOT NULL DEFAULT '',
    lat             REAL,
    lon             REAL,
    work_mode       TEXT NOT NULL CHECK (work_mode IN ('on_site','hybrid','remote')),
    pay_amount      REAL,
    pay_unit        TEXT CHECK (pay_unit IN ('hour','month')),
    pay_note        TEXT NOT NULL DEFAULT '',
    shifts          TEXT NOT NULL DEFAULT '[]',
    schedule_flexible INTEGER NOT NULL DEFAULT 0,
    hours_min       INTEGER,
    hours_max       INTEGER,
    contract        TEXT CHECK (contract IN
        ('permanent','fixed_term','seasonal','gig','summer_job','traineeship')),
    experience      TEXT CHECK (experience IN ('none','some','required')),
    experience_note TEXT NOT NULL DEFAULT '',
    qualifications  TEXT NOT NULL DEFAULT '[]',
    onboarding      TEXT NOT NULL DEFAULT '',
    languages       TEXT NOT NULL DEFAULT '[]',
    lifting         TEXT,
    apply_question  TEXT NOT NULL DEFAULT '',
    cv_required     INTEGER NOT NULL DEFAULT 0,
    positions       INTEGER NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','open','closed')),
    source          TEXT NOT NULL DEFAULT 'employer'
                    CHECK (source IN ('employer','advisor')),
    confirmed_at    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- no row = "Not known yet"; value is only ever yes|no in the table.
CREATE TABLE job_condition (
    job_id     TEXT NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    key        TEXT NOT NULL,
    value      TEXT NOT NULL CHECK (value IN ('yes','no')),
    source     TEXT NOT NULL CHECK (source IN ('employer','advisor')),
    checked_at TEXT,
    note       TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (job_id, key)
);

CREATE TABLE saved_job (
    user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    job_id  TEXT NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, job_id)
);

CREATE TABLE application (
    id                 TEXT PRIMARY KEY,
    job_id             TEXT NOT NULL REFERENCES job(id),
    user_id            TEXT REFERENCES user(id) ON DELETE SET NULL,
    name               TEXT NOT NULL DEFAULT '',
    contact_method     TEXT NOT NULL DEFAULT '',
    contact_value      TEXT NOT NULL DEFAULT '',
    availability_note  TEXT NOT NULL DEFAULT '',
    answer             TEXT NOT NULL DEFAULT '',
    cv_text            TEXT,
    shared_needs       TEXT NOT NULL DEFAULT '[]',
    meet_at_event      INTEGER NOT NULL DEFAULT 0,
    status             TEXT NOT NULL DEFAULT 'sent' CHECK (status IN
        ('sent','interview','offer','not_selected','withdrawn','job_closed')),
    status_note        TEXT NOT NULL DEFAULT '',
    created_by_advisor INTEGER NOT NULL DEFAULT 0,
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE help_request (
    id             TEXT PRIMARY KEY,
    user_id        TEXT REFERENCES user(id) ON DELETE SET NULL,
    name           TEXT NOT NULL DEFAULT '',
    contact_method TEXT NOT NULL DEFAULT '',
    contact_value  TEXT NOT NULL DEFAULT '',
    job_id         TEXT REFERENCES job(id),
    kind           TEXT NOT NULL CHECK (kind IN
        ('check_conditions','prepare_application','arrange_contact','other',
         'employer_support')),
    condition_keys TEXT NOT NULL DEFAULT '[]',
    message        TEXT NOT NULL DEFAULT '',
    consent        INTEGER NOT NULL DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'new'
                   CHECK (status IN ('new','in_progress','done')),
    advisor_id     TEXT REFERENCES user(id),
    advisor_reply  TEXT NOT NULL DEFAULT '',
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    actor      TEXT NOT NULL,
    action     TEXT NOT NULL,
    detail     TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- v3 additions ------------------------------------------------------------

-- cached "simpler version" payloads; invalidated by source_hash on text change
CREATE TABLE job_text_cache (
    job_id      TEXT NOT NULL,
    language    TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (job_id, language)
);

CREATE TABLE commute_cache (
    job_id      TEXT NOT NULL,
    district    TEXT NOT NULL,
    payload     TEXT NOT NULL,
    computed_at TEXT NOT NULL,
    PRIMARY KEY (job_id, district)
);

-- event mode: one 4-digit visitor number per resident per event
CREATE TABLE event_visitor (
    user_id  TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    event_id TEXT NOT NULL REFERENCES event(id),
    code     TEXT NOT NULL,
    PRIMARY KEY (user_id, event_id),
    UNIQUE (event_id, code)
);

CREATE TABLE event_plan (
    user_id     TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    event_id    TEXT NOT NULL REFERENCES event(id),
    employer_id TEXT NOT NULL REFERENCES employer(id),
    added_at    TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, event_id, employer_id)
);

CREATE TABLE event_talk (
    id            TEXT PRIMARY KEY,
    event_id      TEXT NOT NULL REFERENCES event(id),
    user_id       TEXT REFERENCES user(id),  -- NULL = walk-up visitor
    employer_id   TEXT NOT NULL REFERENCES employer(id),
    job_id        TEXT REFERENCES job(id),
    -- walk-up visitor without an account, recorded by an advisor with
    -- the visitor's spoken consent
    visitor_name  TEXT NOT NULL DEFAULT '',
    visitor_contact_method TEXT CHECK (visitor_contact_method IN
        ('phone','sms','email')),
    visitor_contact_value  TEXT NOT NULL DEFAULT '',
    recorded_by   TEXT REFERENCES user(id),
    consent       INTEGER NOT NULL DEFAULT 0,
    status        TEXT NOT NULL CHECK (status IN ('talked','answered')),
    outcome       TEXT CHECK (outcome IN ('next_step','not_now')),
    employer_note TEXT NOT NULL DEFAULT '',
    talked_at     TEXT NOT NULL,
    answered_at   TEXT,
    UNIQUE (event_id, user_id, employer_id)
);
