-- Cafeteria Food Waste Intelligence System
-- PostgreSQL Database Schema

CREATE TYPE waste_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE report_status AS ENUM ('uploaded', 'processing', 'completed', 'failed');

CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(255),
    address VARCHAR(500),
    student_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_path VARCHAR(1000),
    status report_status DEFAULT 'uploaded',
    raw_text TEXT,
    extracted_data TEXT,       -- JSON: structured data from Claude
    ai_analysis TEXT,          -- JSON: waste analysis from Claude
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),     -- entree, side, beverage, dessert, fruit, vegetable, grain, dairy
    servings_prepared INTEGER,
    servings_served INTEGER,
    servings_wasted INTEGER,
    cost_per_serving FLOAT,
    date_served DATE
);

CREATE TABLE waste_records (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    report_id INTEGER REFERENCES reports(id),
    date DATE NOT NULL,
    total_prepared_lbs FLOAT,
    total_served_lbs FLOAT,
    total_wasted_lbs FLOAT,
    waste_percentage FLOAT,
    predicted_waste_level waste_level,
    waste_drivers TEXT,        -- JSON array of identified drivers
    recommendations TEXT,      -- JSON array of recommendations
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_reports_school_id ON reports(school_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_menu_items_report_id ON menu_items(report_id);
CREATE INDEX idx_waste_records_school_id ON waste_records(school_id);
CREATE INDEX idx_waste_records_date ON waste_records(date);
