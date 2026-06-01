-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Space object catalog
CREATE TABLE IF NOT EXISTS catalog (
    id          BIGSERIAL PRIMARY KEY,
    norad_id    VARCHAR(10) UNIQUE,
    name        VARCHAR(255) NOT NULL,
    object_type VARCHAR(50),        -- 'DEBRIS' | 'PAYLOAD' | 'NEO' | 'PLANET'
    diameter_m  FLOAT,
    mass_kg     FLOAT,
    source      VARCHAR(50),        -- 'CELESTRAK' | 'NASA_NEOWS' | 'MPC'
    raw_tle1    TEXT,
    raw_tle2    TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Time-series orbital state vectors (hypertable)
CREATE TABLE IF NOT EXISTS orbital_states (
    time        TIMESTAMPTZ NOT NULL,
    object_id   BIGINT REFERENCES catalog(id) ON DELETE CASCADE,
    x_km        DOUBLE PRECISION NOT NULL,
    y_km        DOUBLE PRECISION NOT NULL,
    z_km        DOUBLE PRECISION NOT NULL,
    vx_km_s     DOUBLE PRECISION NOT NULL,
    vy_km_s     DOUBLE PRECISION NOT NULL,
    vz_km_s     DOUBLE PRECISION NOT NULL,
    altitude_km DOUBLE PRECISION,
    coord_frame VARCHAR(20) DEFAULT 'GEOCENTRIC'
);

SELECT create_hypertable('orbital_states', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_orbital_states_object_time
    ON orbital_states (object_id, time DESC);

-- Conjunction / collision risk events
CREATE TABLE IF NOT EXISTS conjunctions (
    id              BIGSERIAL PRIMARY KEY,
    primary_id      BIGINT REFERENCES catalog(id),
    secondary_id    BIGINT REFERENCES catalog(id),
    tca             TIMESTAMPTZ NOT NULL,      -- Time of Closest Approach
    miss_distance_m DOUBLE PRECISION NOT NULL,
    pc              DOUBLE PRECISION NOT NULL, -- Probability of Collision
    risk_level      VARCHAR(20),               -- 'SAFE' | 'WARNING' | 'CRITICAL'
    computed_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conjunctions_tca ON conjunctions (tca DESC);
CREATE INDEX IF NOT EXISTS idx_conjunctions_pc  ON conjunctions (pc DESC);

-- AI prediction outputs
CREATE TABLE IF NOT EXISTS predictions (
    id              BIGSERIAL PRIMARY KEY,
    object_id       BIGINT REFERENCES catalog(id),
    predicted_at    TIMESTAMPTZ NOT NULL,
    horizon_hours   INTEGER DEFAULT 72,
    trajectory_json JSONB,       -- predicted x,y,z arrays
    anomaly_score   FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);