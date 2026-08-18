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