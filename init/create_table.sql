CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255),
    product_name VARCHAR(255),
    input_url TEXT,
    output_url TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
