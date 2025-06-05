DROP VIEW IF EXISTS game_scores;
DROP TABLE IF EXISTS was_played_in;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;



CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    gpa FLOAT NOT NULL
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL
);

CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
    
CREATE TABLE was_played_in (
    game_id INT NOT NULL,
    course_id INT NOT NULL,
    placement INT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    PRIMARY KEY (game_id, placement)
);

CREATE VIEW game_scores AS 
SELECT count(*)-2 AS score, game_id FROM was_played_in
GROUP BY game_id;

\copy courses (title, gpa) FROM 'data.csv' DELIMITER ',' CSV HEADER;

