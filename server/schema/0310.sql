-- drop database first just it already exists, else there will be errors
DROP DATABASE IF EXISTS dsa4213;
CREATE DATABASE dsa4213;
USE dsa4213;

-- drop table first if it already exists else we can't use it 
DROP TABLE IF EXISTS candidates CASCADE;

-- create candidate table
CREATE TABLE candidates (
	candidate_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    candidate_rank INT NOT NULL CHECK (candidate_rank > 0) DEFAULT 1,
    candidate_name VARCHAR(50) NOT NULL,
    -- candidate_age INT CHECK (candidate_age > 0 AND candidate_age < 100),
    -- candidate_experience ENUM ('Entry', 'Mid', 'Senior'),
    -- candidate_gender ENUM ('Male', 'Female', 'Other'),
    candidate_MostRecenJobTitle VARCHAR(255),
    candidate_education VARCHAR(255),
    candidate_strength VARCHAR(1000),
    candidate_MostRescentJobTime VARCHAR(255),
    candidate_workAttitude FLOAT(8,2),
    candidate_adaptability FLOAT(8,2),
    candidate_collaboration FLOAT(8,2),
    candidate_workEthics FLOAT(8,2),
    candidate_leaderShip FLOAT(8,2)

    -- TODO: discuss what other columns to add
);


