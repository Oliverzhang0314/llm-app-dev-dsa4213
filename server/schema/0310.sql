-- drop database first just it already exists, else there will be errors
DROP DATABASE IF EXISTS dsa4213;
CREATE DATABASE dsa4213;
USE dsa4213;

-- drop table first if it already exists else we can't use it 
DROP TABLE IF EXISTS candidates CASCADE;

-- create candidate table
CREATE TABLE candidates (
	candidate_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    candidate_name VARCHAR(50) NOT NULL,
    candidate_gender VARCHAR(50) NOT NULL,
    candidate_experience INT,
    candidate_MostRecenJobTitle VARCHAR(255),
    candidate_education VARCHAR(255),
    candidate_strength VARCHAR(1000),
    candidate_MostRescentJobTime VARCHAR(255),
    candidate_workAttitude FLOAT(8,2),
    candidate_adaptability FLOAT(8,2),
    candidate_collaboration FLOAT(8,2),
    candidate_communication FLOAT(8,2),
    candidate_workEthics FLOAT(8,2),
    candidate_leaderShip FLOAT(8,2),
    
    position_applied VARCHAR(50),
	region VARCHAR(50),
	department VARCHAR(50)

    -- TODO: discuss what other columns to add
);


