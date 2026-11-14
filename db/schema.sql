-- TalentMatch Signal — SQLite schema (synthetic data only, constraint C2)
-- The API rebuilds db/talentmatch.sqlite from this file + db/seed/*.json on
-- startup whenever the database file is missing.

CREATE TABLE IF NOT EXISTS event (
    id                   TEXT PRIMARY KEY,
    name                 TEXT NOT NULL,
    date                 TEXT NOT NULL,           -- ISO 8601 date
    format               TEXT NOT NULL,
    companies_declared   INTEGER NOT NULL,
    talents_registered   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS company (
    id            TEXT PRIMARY KEY,
    event_id      TEXT NOT NULL REFERENCES event(id),
    name          TEXT NOT NULL,
    size          INTEGER NOT NULL,
    city          TEXT NOT NULL,
    contact_name  TEXT NOT NULL,
    slots         INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS challenge_card (
    id                     TEXT PRIMARY KEY,
    company_id             TEXT NOT NULL REFERENCES company(id),
    title                  TEXT NOT NULL,
    problem_90d            TEXT NOT NULL,
    nice_to_haves          TEXT NOT NULL DEFAULT '[]',  -- JSON array of strings
    languages              TEXT NOT NULL DEFAULT '[]',  -- JSON array of LanguageNeed
    work_mode              TEXT NOT NULL DEFAULT '',
    status                 TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved')),
    company_minutes_spent  INTEGER NOT NULL DEFAULT 0,
    created_at             TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS card_requirement (
    id           TEXT PRIMARY KEY,
    card_id      TEXT NOT NULL REFERENCES challenge_card(id) ON DELETE CASCADE,
    position     INTEGER NOT NULL DEFAULT 0,
    text         TEXT NOT NULL,
    how_we_check TEXT NOT NULL DEFAULT '',
    esco_uri     TEXT,
    esco_label   TEXT
);
CREATE INDEX IF NOT EXISTS idx_card_req ON card_requirement(card_id);

CREATE TABLE IF NOT EXISTS talent (
    id            TEXT PRIMARY KEY,          -- e.g. 'ta-0427'
    pseudonym     TEXT NOT NULL,             -- e.g. 'Talent #0427' — never the name
    languages     TEXT NOT NULL DEFAULT '[]',-- JSON [{language, level}]
    availability  TEXT NOT NULL DEFAULT '',
    pool_consent  INTEGER NOT NULL DEFAULT 0 -- pool bands count only consenting talents
);

-- Kept strictly apart from `talent`; joined only after a mutual yes (Spark accept).
CREATE TABLE IF NOT EXISTS talent_identity (
    talent_id  TEXT PRIMARY KEY REFERENCES talent(id),
    name       TEXT NOT NULL,
    city       TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS evidence_card (
    talent_id  TEXT PRIMARY KEY REFERENCES talent(id),
    headline   TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS evidence_claim (
    id                TEXT PRIMARY KEY,
    talent_id         TEXT NOT NULL REFERENCES talent(id),
    text              TEXT NOT NULL,
    quote             TEXT NOT NULL,          -- verbatim words of the talent ("no quote, no claim")
    esco_uri          TEXT,
    esco_label        TEXT,
    evidence_level    TEXT NOT NULL DEFAULT 'own words'
                      CHECK (evidence_level IN ('own words','artefact','witnessed live')),
    confirmed         INTEGER NOT NULL DEFAULT 0,
    original_language TEXT NOT NULL DEFAULT 'en',
    translated        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_claim_talent ON evidence_claim(talent_id);
CREATE INDEX IF NOT EXISTS idx_claim_esco   ON evidence_claim(esco_uri);

-- Short-lived, quote-checked proposals issued by the server. No raw transcript
-- is stored; only the exact claims a person may choose to confirm.
CREATE TABLE IF NOT EXISTS evidence_proposal (
    id            TEXT PRIMARY KEY,
    talent_id     TEXT NOT NULL REFERENCES talent(id),
    payload       TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_proposal_talent ON evidence_proposal(talent_id);

CREATE TABLE IF NOT EXISTS spark (
    id             TEXT PRIMARY KEY,
    talent_id      TEXT NOT NULL REFERENCES talent(id),
    card_id        TEXT NOT NULL REFERENCES challenge_card(id),
    claim_id       TEXT NOT NULL REFERENCES evidence_claim(id),
    requirement_id TEXT NOT NULL REFERENCES card_requirement(id),
    note           TEXT,
    status         TEXT NOT NULL DEFAULT 'sent'
                   CHECK (status IN ('sent','accepted','declined','refunded')),
    deadline       TEXT NOT NULL,           -- ISO 8601; unanswered past this -> refunded
    reason_chip    TEXT,
    revealed_name  TEXT,                    -- filled on accept only
    slot           TEXT,                    -- filled on accept only
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_spark_talent ON spark(talent_id);
CREATE INDEX IF NOT EXISTS idx_spark_card   ON spark(card_id);

CREATE TABLE IF NOT EXISTS meeting (
    id         TEXT PRIMARY KEY,
    spark_id   TEXT NOT NULL REFERENCES spark(id),
    company_id TEXT NOT NULL REFERENCES company(id),
    card_id    TEXT NOT NULL REFERENCES challenge_card(id),
    talent_id  TEXT NOT NULL REFERENCES talent(id),
    slot       TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS conversation_tick (
    meeting_id      TEXT NOT NULL REFERENCES meeting(id),
    requirement_id  TEXT NOT NULL REFERENCES card_requirement(id),
    seen            INTEGER NOT NULL DEFAULT 0,
    note            TEXT,
    PRIMARY KEY (meeting_id, requirement_id)
);

CREATE TABLE IF NOT EXISTS closure (
    id                   TEXT PRIMARY KEY,
    meeting_id           TEXT NOT NULL REFERENCES meeting(id),
    outcome              TEXT NOT NULL CHECK (outcome IN ('next_step','not_now')),
    reason_chips         TEXT NOT NULL DEFAULT '[]',   -- JSON array
    next_step            TEXT,
    redirect_company_id  TEXT,
    message_to_talent    TEXT NOT NULL DEFAULT '',
    support_banner       TEXT,
    created_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    at      TEXT NOT NULL DEFAULT (datetime('now')),
    actor   TEXT NOT NULL CHECK (actor IN ('ai','human')),
    action  TEXT NOT NULL,
    detail  TEXT NOT NULL DEFAULT ''
);
