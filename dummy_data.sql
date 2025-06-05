INSERT INTO users (username, hashed_password, salt)
VALUES 
('alice', 'hashed_pw1', 'salt1'),
('bob', 'hashed_pw2', 'salt2'),
('charlie', 'hashed_pw3', 'salt3'),
('Test123123', '6ca1f47afa062b1bf7a38c4bb8cd7effd271d2e55f66623f083f3a481f80bc35', '814276f5e7c692b371fc39dfac1eeda9');


INSERT INTO games (user_id) VALUES (1); -- Alice's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(1, 10, 1),
(1, 3, 2),
(1, 2, 3),
(1, 4, 4),
(1, 5, 5),
(1, 6, 6),
(1, 7, 7),
(1, 8, 8),
(1, 9, 9);

INSERT INTO games (user_id) VALUES (1); -- Alice's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(2, 10, 1),
(2, 3, 2);

INSERT INTO games (user_id) VALUES (1); -- Alice's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(3, 10, 1),
(3, 3, 2);


INSERT INTO games (user_id) VALUES (2);  -- Bob's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(4, 6, 1),
(4, 7, 2),
(4, 8, 3);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(5, 3, 1),
(5, 1, 2),
(5, 2, 3),
(5, 6, 4);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(6, 3, 1),
(6, 1, 2),
(6, 2, 3),
(6, 6, 4),
(6, 7, 5),
(6, 8, 6),
(6, 9, 7),
(6, 10, 8),
(6, 11, 9),
(6, 12, 10),
(6, 13, 11),
(6, 14, 12);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(7, 3, 1),
(7, 1, 2);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(8, 3, 1),
(8, 1, 2);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(9, 3, 1),
(9, 1, 2);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(10, 3, 1),
(10, 1, 2);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(11, 3, 1),
(11, 1, 2);

INSERT INTO games (user_id) VALUES (3);  -- Charlie's game

INSERT INTO was_played_in (game_id, course_id, placement)
VALUES
(12, 3, 1),
(12, 1, 2);

