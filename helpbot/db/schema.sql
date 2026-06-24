CREATE TABLE IF NOT EXISTS orders (
    order_id        TEXT PRIMARY KEY,
    status          TEXT NOT NULL,
    carrier         TEXT,
    tracking        TEXT,
    estimated_delivery  TEXT,
    estimated_dispatch  TEXT,
    delivered_on    TEXT
);

CREATE TABLE IF NOT EXISTS return_eligibility (
    order_id        TEXT PRIMARY KEY,
    eligible        INTEGER NOT NULL,
    reason          TEXT NOT NULL,
    delivered_on    TEXT
);

CREATE TABLE IF NOT EXISTS refunds (
    order_id        TEXT PRIMARY KEY,
    stage           TEXT NOT NULL,
    amount          REAL NOT NULL,
    method          TEXT NOT NULL,
    paid_on         TEXT,
    expected_payment TEXT,
    received_on     TEXT
);

CREATE TABLE IF NOT EXISTS books (
    title           TEXT PRIMARY KEY,
    status          TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    formats         TEXT NOT NULL,
    restock_date    TEXT,
    restock_confidence TEXT
);

CREATE TABLE IF NOT EXISTS accounts (
    email           TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    status          TEXT NOT NULL,
    reason          TEXT,
    unlock_url      TEXT
);

CREATE TABLE IF NOT EXISTS promo_codes (
    code            TEXT PRIMARY KEY,
    valid           INTEGER NOT NULL,
    discount        TEXT,
    expires         TEXT,
    applicable_to   TEXT,
    reason          TEXT,
    expired_on      TEXT
);

CREATE TABLE IF NOT EXISTS loyalty (
    email               TEXT PRIMARY KEY,
    points              INTEGER NOT NULL,
    tier                TEXT NOT NULL,
    points_to_next_tier INTEGER
);

CREATE TABLE IF NOT EXISTS digital_purchases (
    email           TEXT NOT NULL,
    product_title   TEXT NOT NULL,
    owned           INTEGER NOT NULL,
    link_status     TEXT,
    downloads_remaining INTEGER,
    expires         TEXT,
    expired_on      TEXT,
    PRIMARY KEY (email, product_title)
);

CREATE TABLE IF NOT EXISTS gift_orders (
    gift_code           TEXT PRIMARY KEY,
    status              TEXT NOT NULL,
    recipient_name      TEXT NOT NULL,
    recipient_email     TEXT NOT NULL,
    items               TEXT NOT NULL,
    delivered_on        TEXT,
    estimated_delivery  TEXT,
    estimated_dispatch  TEXT
);
