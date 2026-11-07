
USE campus_complaints;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    college_id VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'STAFF', 'ADMIN') NOT NULL DEFAULT 'USER',
    department VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    complaint_text VARCHAR(2000) NOT NULL,
    category VARCHAR(100) NOT NULL DEFAULT 'Other',
    category_confidence DECIMAL(5,4) NULL,
    priority ENUM('HIGH', 'MEDIUM', 'LOW') NOT NULL DEFAULT 'MEDIUM',
    priority_reason VARCHAR(500) NOT NULL,
    location VARCHAR(100) NOT NULL,
    image_path VARCHAR(500) NULL,
    assigned_department VARCHAR(100) NOT NULL,
    assigned_staff BIGINT UNSIGNED NULL,
    status ENUM(
        'Pending',
        'Assigned',
        'In Progress',
        'Resolved',
        'Rejected'
    ) NOT NULL DEFAULT 'Pending',
    resolution_note TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_complaints_user
        FOREIGN KEY (user_id) REFERENCES users(id),

    CONSTRAINT fk_complaints_assigned_staff
        FOREIGN KEY (assigned_staff) REFERENCES users(id),

    INDEX idx_complaints_user_created (user_id, created_at),
    INDEX idx_complaints_department_status (assigned_department, status),
    INDEX idx_complaints_priority_created (priority, created_at),
    INDEX idx_complaints_category (category),
    INDEX idx_complaints_location (location)
);
