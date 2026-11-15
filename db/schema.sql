-- Espoo Work Map — SQLite schema (spec section 2). Synthetic data only.
-- Bump `PRAGMA user_version` in app/api/db.py when this file changes.

PRAGMA user_version = 14;

CREATE TABLE user (
    id            TEXT PRIMARY KEY,
    email         TEXT UNIQUE,
    phone         TEXT,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('resident','employer','advisor')),
    name          TEXT NOT NULL DEFAULT '',
    employer_id   TEXT REFERENCES employer(id),
    share_email   INTEGER NOT NULL DEFAULT 0,
    share_phone   INTEGER NOT NULL DEFAULT 0,
    public_link   TEXT NOT NULL DEFAULT '',
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
    about              TEXT NOT NULL DEFAULT '',
    share_email        INTEGER NOT NULL DEFAULT 0,
    share_phone        INTEGER NOT NULL DEFAULT 0,
    public_link        TEXT NOT NULL DEFAULT ''
);

CREATE TABLE employer (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    about         TEXT NOT NULL DEFAULT '',
    contact_name  TEXT NOT NULL DEFAULT '',
    contact_email TEXT NOT NULL DEFAULT '',
    contact_phone TEXT NOT NULL DEFAULT '',
    tagline       TEXT NOT NULL DEFAULT '',
    field         TEXT NOT NULL DEFAULT '',
    district      TEXT NOT NULL DEFAULT '',
    address       TEXT NOT NULL DEFAULT '',
    size_band     TEXT NOT NULL DEFAULT '',
    founded       INTEGER,
    work_languages TEXT NOT NULL DEFAULT '[]',
    logo_color    TEXT NOT NULL DEFAULT '',
    how_we_welcome TEXT NOT NULL DEFAULT ''
);

CREATE TABLE event (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    date         TEXT NOT NULL,
    venue        TEXT NOT NULL DEFAULT '',
    advisor_note TEXT NOT NULL DEFAULT '',
    format       TEXT NOT NULL DEFAULT 'in_person'
                 CHECK (format IN ('in_person','online')),
    series       TEXT NOT NULL DEFAULT '',
    language     TEXT NOT NULL DEFAULT 'fi',
    starts_at    TEXT NOT NULL DEFAULT '',
    ends_at      TEXT NOT NULL DEFAULT '',
    address      TEXT NOT NULL DEFAULT '',
    description  TEXT NOT NULL DEFAULT '',
    programme    TEXT NOT NULL DEFAULT '[]',
    capacity     INTEGER NOT NULL DEFAULT 0,
    slot_minutes INTEGER NOT NULL DEFAULT 10,
    need_deadline TEXT NOT NULL DEFAULT '',
    publish_date TEXT NOT NULL DEFAULT '',
    registration_opens TEXT NOT NULL DEFAULT '',
    matching_closes  TEXT NOT NULL DEFAULT '',
    answers_due      TEXT NOT NULL DEFAULT '',
    time_groups  TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE employer_event (
    employer_id TEXT NOT NULL REFERENCES employer(id),
    event_id    TEXT NOT NULL REFERENCES event(id),
    booth       TEXT NOT NULL DEFAULT '',
    need_card        TEXT,
    need_submitted_at TEXT,
    need_by          TEXT CHECK (need_by IN ('employer','advisor')),
    slots            INTEGER NOT NULL DEFAULT 0,
    formats          TEXT NOT NULL DEFAULT '[]',
    reminders_sent   INTEGER NOT NULL DEFAULT 0,
    last_reminder_at TEXT,
    PRIMARY KEY (employer_id, event_id)
);

-- talent registered for an event; card = what they have done in own words
CREATE TABLE talent_registration (
    id          TEXT PRIMARY KEY,
    event_id    TEXT NOT NULL REFERENCES event(id),
    user_id     TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    time_group  TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL CHECK (status IN
                ('registered','waitlist','cancelled')),
    card_language TEXT NOT NULL DEFAULT 'en',
    card        TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (event_id, user_id)
);

-- employer interest in an anonymous talent card
CREATE TABLE event_invite (
    event_id        TEXT NOT NULL REFERENCES event(id),
    employer_id     TEXT NOT NULL REFERENCES employer(id),
    registration_id TEXT NOT NULL REFERENCES talent_registration(id),
    simulated       INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (event_id, employer_id, registration_id)
);

-- booked when interest and invite are mutual
CREATE TABLE event_meeting (
    id          TEXT PRIMARY KEY,
    event_id    TEXT NOT NULL REFERENCES event(id),
    employer_id TEXT NOT NULL REFERENCES employer(id),
    user_id     TEXT NOT NULL REFERENCES user(id),
    registration_id TEXT REFERENCES talent_registration(id),
    starts_at   TEXT NOT NULL,
    video_url   TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL CHECK (status IN
                ('booked','done','no_show','cancelled'))
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
    break_min       INTEGER NOT NULL DEFAULT 0,
    rota            INTEGER NOT NULL DEFAULT 0,
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
    commitments     TEXT NOT NULL DEFAULT '[]',
    positions       INTEGER NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','open','closed')),
    contract_id     TEXT REFERENCES procurement_contract(id),
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
    meets_must_haves   INTEGER NOT NULL DEFAULT 0,
    wants_tryout       INTEGER NOT NULL DEFAULT 0,
    contract_eligible  INTEGER NOT NULL DEFAULT 0,
    shared_credentials TEXT NOT NULL DEFAULT '[]',
    shared_event_records TEXT NOT NULL DEFAULT '[]',
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
         'employer_support','check_document')),
    condition_keys TEXT NOT NULL DEFAULT '[]',
    document_label TEXT NOT NULL DEFAULT '',
    message        TEXT NOT NULL DEFAULT '',
    consent        INTEGER NOT NULL DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'new'
                   CHECK (status IN ('new','in_progress','done')),
    advisor_id     TEXT REFERENCES user(id),
    advisor_reply  TEXT NOT NULL DEFAULT '',
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE procurement_contract (
    id              TEXT PRIMARY KEY,
    employer_id     TEXT NOT NULL REFERENCES employer(id),
    title           TEXT NOT NULL,
    value_eur       REAL NOT NULL DEFAULT 0,
    starts          TEXT NOT NULL,
    ends            TEXT NOT NULL,
    due             TEXT NOT NULL,
    hires_required  INTEGER NOT NULL,
    hires_done      INTEGER NOT NULL DEFAULT 0,
    target_groups   TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE contract_hire (
    id           TEXT PRIMARY KEY,
    contract_id  TEXT NOT NULL REFERENCES procurement_contract(id),
    hired_on     TEXT NOT NULL,
    note         TEXT NOT NULL DEFAULT '',
    advisor_id   TEXT REFERENCES user(id),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE credential (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    label       TEXT NOT NULL,
    advisor_id  TEXT REFERENCES user(id),
    checked_at  TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
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
    meets           TEXT NOT NULL DEFAULT '[]',
    language_levels TEXT NOT NULL DEFAULT '{}',
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
    next_kind     TEXT CHECK (next_kind IN ('interview','tryout','call')),
    next_at       TEXT,
    next_place    TEXT NOT NULL DEFAULT '',
    talent_response TEXT CHECK (talent_response IN ('confirmed','other_time')),
    talent_response_note TEXT NOT NULL DEFAULT '',
    meeting_id    TEXT REFERENCES event_meeting(id),
    observed      TEXT NOT NULL DEFAULT '[]',
    employer_note TEXT NOT NULL DEFAULT '',
    simulated     INTEGER NOT NULL DEFAULT 0,
    talked_at     TEXT NOT NULL,
    answered_at   TEXT,
    UNIQUE (event_id, user_id, employer_id)
);

-- demo clock (v13): demo mode reads "now" from here
CREATE TABLE demo_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- walk-in queue at a booth (v10)
CREATE TABLE event_queue (
    event_id     TEXT NOT NULL REFERENCES event(id),
    employer_id  TEXT NOT NULL REFERENCES employer(id),
    user_id      TEXT NOT NULL REFERENCES user(id),
    joined_at    TEXT NOT NULL DEFAULT (datetime('now')),
    status       TEXT NOT NULL DEFAULT 'waiting' CHECK (status IN
        ('waiting','called','left')),
    PRIMARY KEY (event_id, employer_id, user_id)
);

-- personal QR pass for event participants (v11)
CREATE TABLE event_pass (
    token      TEXT PRIMARY KEY,
    event_id   TEXT NOT NULL REFERENCES event(id),
    user_id    TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (event_id, user_id)
);

-- one row per scan of a pass (v11)
CREATE TABLE event_scan (
    id         TEXT PRIMARY KEY,
    event_id   TEXT NOT NULL REFERENCES event(id),
    scanner_id TEXT NOT NULL REFERENCES user(id),
    scanned_id TEXT NOT NULL REFERENCES user(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (event_id, scanner_id, scanned_id)
);

-- positive-only badges; person controls visibility (v11)
CREATE TABLE badge (
    id          TEXT PRIMARY KEY,
    user_id     TEXT REFERENCES user(id) ON DELETE CASCADE,
    employer_id TEXT REFERENCES employer(id),
    event_id    TEXT NOT NULL REFERENCES event(id),
    kind        TEXT NOT NULL CHECK (kind IN
        ('attended','kudos','hired','organizer','employer_answered')),
    label       TEXT NOT NULL DEFAULT '',
    note        TEXT NOT NULL DEFAULT '',
    given_by    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    hidden      INTEGER NOT NULL DEFAULT 0,
    UNIQUE (user_id, employer_id, event_id, kind, label)
);

-- connections between event participants (v11)
CREATE TABLE connection (
    user_a     TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    user_b     TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    event_id   TEXT NOT NULL REFERENCES event(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    note_a     TEXT NOT NULL DEFAULT '',
    note_b     TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (user_a, user_b, event_id)
);

-- virtual booth Q&A board (v14, online events §9.7)
CREATE TABLE event_question (
    id          TEXT PRIMARY KEY,
    event_id    TEXT NOT NULL REFERENCES event(id),
    employer_id TEXT NOT NULL REFERENCES employer(id),
    user_id     TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    answer      TEXT,
    answered_by TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    answered_at TEXT
);

-- networking lounge membership (v14, online events §9.7)
CREATE TABLE lounge_member (
    event_id  TEXT NOT NULL REFERENCES event(id),
    user_id   TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    joined_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (event_id, user_id)
);

PRAGMA user_version = 14;
