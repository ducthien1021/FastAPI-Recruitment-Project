CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    fullname VARCHAR(255),
    role_code VARCHAR(50) NOT NULL DEFAULT 'HR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE department (
    department_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL UNIQUE,
    desc VARCHAR(500)
);

CREATE TABLE job (
    job_id VARCHAR(36) PRIMARY KEY,        -- UUID chuẩn dài 36 ký tự
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100) NOT NULL UNIQUE,
    desc VARCHAR(500)
);

CREATE TABLE "recruitment_proposal" (
	"recruitment_proposal_id"	VARCHAR(36),
	"code"	VARCHAR(100) NOT NULL UNIQUE,
	"title"	VARCHAR(255) NOT NULL,
	"desc"	VARCHAR(1000),
	"skills"	VARCHAR(1000),
	"quantity"	INTEGER,
	"start_date"	VARCHAR(10),
	"end_date"	VARCHAR(10),
	"location"	VARCHAR(255),
	"status"	VARCHAR(20) CHECK("status" IN ('approve', 'reject', 'pending', 'done')),
	"job_id"	VARCHAR(36),
	"job_type"	VARCHAR(100),
	"department_id"	VARCHAR(36),
	"salary_start"	REAL,
	"salary_end"	REAL,
	"benefits"	VARCHAR(1000),
	"user_id"	VARCHAR(36),
	PRIMARY KEY("recruitment_proposal_id")
)

CREATE TABLE recruitment_proposal_history (
    recruitment_proposal_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recruitment_proposal_id VARCHAR(36) NOT NULL,
    status VARCHAR(100),
    change_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidates (
    candidate_id VARCHAR(36) PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone VARCHAR(20),
    gender VARCHAR(10),
    date_of_birth DATE,
    recruitment_proposal_id VARCHAR(36) NOT NULL,
    cv_file VARCHAR(255)
);
