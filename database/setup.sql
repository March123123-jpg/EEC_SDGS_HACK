-- Table: zones

-- DROP TABLE IF EXISTS zones;

CREATE TABLE IF NOT EXISTS zones (

    id SERIAL PRIMARY KEY,

    device_code VARCHAR(100) UNIQUE NOT NULL,

    name VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_readings (

    id SERIAL PRIMARY KEY,

    zone_id INTEGER NOT NULL,

    temperature_c DOUBLE PRECISION NOT NULL,

    humidity_pct DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sensor_zone

        FOREIGN KEY (zone_id)

        REFERENCES zones(id)

        ON DELETE CASCADE
);

-- Table: risk_records

-- DROP TABLE IF EXISTS risk_records;

CREATE TABLE IF NOT EXISTS risk_records
(
    id serial PRIMARY KEY,
    reading_id INTEGER NOT NULL,
    wbgt DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(30) NOT NULL,
    work_rest_regimen VARCHAR(20),
    recommendation TEXT,
    risk_value numeric(5,2) NOT NULL,
    recommendation character varying(255) COLLATE pg_catalog."default",
    "timestamp" timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT risk_records_pkey PRIMARY KEY (id),
    CONSTRAINT risk_records_reading_id_fkey FOREIGN KEY (reading_id)
        REFERENCES sensor_readings (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT risk_records_risk_level_check CHECK (risk_level::text = ANY (ARRAY['SAFE'::character varying, 'CAUTION'::character varying, 'WARNING'::character varying, 'DANGER'::character varying]::text[]))
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS risk_records
    OWNER to postgres;
-- Index: idx_risk_reading

-- DROP INDEX IF EXISTS idx_risk_reading;

CREATE INDEX IF NOT EXISTS idx_risk_reading
    ON risk_records USING btree
    (reading_id ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE TABLE IF NOT EXISTS alerts (

    id SERIAL PRIMARY KEY,

    zone_id INTEGER NOT NULL,

    risk_level VARCHAR(30) NOT NULL,

    message TEXT NOT NULL,

    status VARCHAR(30) DEFAULT 'NEW',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alert_zone

        FOREIGN KEY (zone_id)

        REFERENCES zones(id)

        ON DELETE CASCADE
);