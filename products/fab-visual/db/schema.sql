-- FAB.VISUAL constitutional central database, offline/portable research snapshot v0.1.
-- SQLite 3.37+ recommended. The Google Sheet remains authoritative for gate
-- statuses until a separate explicit constitutional promotion.
PRAGMA foreign_keys = ON;
PRAGMA application_id = 1178687537;
PRAGMA user_version = 1;

CREATE TABLE IF NOT EXISTS metadata(
 key TEXT PRIMARY KEY NOT NULL,
 value TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS sources(
 source_id TEXT PRIMARY KEY NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('UPSTREAM_GIT','NATIVE_SHEET','GITHUB','GOOGLE_DRIVE','DERIVED_RECORD')),
 uri TEXT NOT NULL,
 pinned_revision TEXT,
 sha256 TEXT CHECK(sha256 IS NULL OR (length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*')),
 authority TEXT NOT NULL CHECK(authority IN ('ORIGINAL_IMMUTABLE','SHEET_AUTHORITATIVE','EVIDENCE_REFERENCE','DERIVED_ONLY'))
) STRICT;

CREATE TABLE IF NOT EXISTS gate_events(
 event_id TEXT PRIMARY KEY NOT NULL CHECK(length(event_id)=64),
 gate_id TEXT NOT NULL,
 ordinal INTEGER NOT NULL CHECK(ordinal>=1),
 status TEXT NOT NULL CHECK(status IN ('PASS','FAIL','NOT_RUN','HOLD','INCONCLUSIVE')),
 predicate TEXT NOT NULL,
 evidence_class TEXT NOT NULL,
 evidence_uri TEXT NOT NULL,
 change_authority TEXT NOT NULL,
 next_proof TEXT NOT NULL,
 implications TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(source_id),
 captured_as_of TEXT NOT NULL,
 UNIQUE(gate_id,ordinal)
) STRICT;

CREATE INDEX IF NOT EXISTS ix_gate_status ON gate_events(status);
CREATE INDEX IF NOT EXISTS ix_gate_id_ordinal ON gate_events(gate_id,ordinal DESC);

CREATE TABLE IF NOT EXISTS evidence(
 evidence_id TEXT PRIMARY KEY NOT NULL CHECK(length(evidence_id)=64),
 title TEXT NOT NULL,
 scope TEXT NOT NULL,
 result TEXT NOT NULL,
 uri TEXT NOT NULL,
 limitations TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(source_id)
) STRICT;

CREATE INDEX IF NOT EXISTS ix_evidence_uri ON evidence(uri);

CREATE TABLE IF NOT EXISTS ci_runs(
 run_id INTEGER PRIMARY KEY CHECK(run_id > 0),
 source_head TEXT NOT NULL CHECK(length(source_head)=40),
 original_pin TEXT NOT NULL CHECK(length(original_pin)=40),
 github_uri TEXT NOT NULL,
 result TEXT NOT NULL CHECK(result IN ('PASS','FAIL','NOT_RUN')),
 grade TEXT NOT NULL CHECK(grade IN ('SOURCE_LOCK','SYNTHETIC','INSTRUMENTED_DERIVATIVE','RENDERER_READBACK')),
 release TEXT NOT NULL CHECK(release='HOLD'),
 provenance_source_id TEXT NOT NULL REFERENCES sources(source_id)
) STRICT;

CREATE TABLE IF NOT EXISTS checkpoint_events(
 checkpoint_id TEXT PRIMARY KEY NOT NULL CHECK(length(checkpoint_id)=64),
 scene TEXT NOT NULL CHECK(scene IN ('raptor-light','turning-light')),
 source_head TEXT NOT NULL CHECK(length(source_head)=40),
 source_html_sha256 TEXT NOT NULL CHECK(length(source_html_sha256)=64),
 derivative_sha256 TEXT NOT NULL CHECK(length(derivative_sha256)=64),
 mode TEXT NOT NULL CHECK(mode IN ('MINIMAL_DERIVATIVE','OBSERVING_DERIVATIVE','CONTROLLED_FIXTURE')),
 applied_update_ordinal INTEGER NOT NULL CHECK(applied_update_ordinal>0),
 source_state_sha256 TEXT CHECK(source_state_sha256 IS NULL OR length(source_state_sha256)=64),
 frame_attestation TEXT NOT NULL CHECK(frame_attestation='NOT_ADMITTED'),
 depth_attestation TEXT NOT NULL CHECK(depth_attestation='NOT_RUN'),
 evidence_uri TEXT NOT NULL,
 provenance_source_id TEXT NOT NULL REFERENCES sources(source_id)
) STRICT;

CREATE VIEW IF NOT EXISTS gate_current AS
SELECT g.* FROM gate_events g WHERE NOT EXISTS (
  SELECT 1 FROM gate_events newer
  WHERE newer.gate_id = g.gate_id AND newer.ordinal > g.ordinal
);
CREATE VIEW IF NOT EXISTS gate_counts AS
SELECT status, count(*) AS total FROM gate_current GROUP BY status;

CREATE TRIGGER IF NOT EXISTS block_gate_update BEFORE UPDATE ON gate_events
BEGIN SELECT RAISE(ABORT,'gate events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_gate_delete BEFORE DELETE ON gate_events
BEGIN SELECT RAISE(ABORT,'gate events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_evidence_update BEFORE UPDATE ON evidence
BEGIN SELECT RAISE(ABORT,'evidence records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_evidence_delete BEFORE DELETE ON evidence
BEGIN SELECT RAISE(ABORT,'evidence records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_checkpoint_update BEFORE UPDATE ON checkpoint_events
BEGIN SELECT RAISE(ABORT,'checkpoint evidence is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_checkpoint_delete BEFORE DELETE ON checkpoint_events
BEGIN SELECT RAISE(ABORT,'checkpoint evidence is append-only'); END;
