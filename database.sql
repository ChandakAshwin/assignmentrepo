CREATE TABLE managers (
    manager_id UUID PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    mob_num VARCHAR(15) NOT NULL,
    pan_num VARCHAR(10) NOT NULL,
    manager_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (manager_id) REFERENCES managers(manager_id)
);
INSERT INTO managers (manager_id, full_name) VALUES
('1', 'Manager One'),
('2', 'Manager Two');
