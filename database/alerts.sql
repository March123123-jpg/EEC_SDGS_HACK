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