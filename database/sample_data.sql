-- Users
INSERT INTO users (username, major, interests) VALUES
('Alice', 'Data Science', 'AI, Python'),
('Bob', 'Cybersecurity', 'Hacking, Networks'),
('Charlie', 'Software Engineering', 'Java, Web Dev'),
('Diana', 'Business IT', 'UX, Design Thinking'),
('Ethan', 'Cloud Computing', 'AWS, Azure'),
('Fatima', 'Machine Learning', 'Deep Learning, NLP');

-- Posts
INSERT INTO posts (user_id, content, timestamp) VALUES
(1, 'Excited to start this semester!', '2025-03-01 10:00'),
(2, 'Anyone wants to form a study group for DAT220?', '2025-03-02 14:30'),
(3, 'Check out my new blog on software design!', '2025-03-03 09:15'),
(4, 'Does anyone have notes for last lecture?', '2025-03-04 13:45'),
(5, 'I just passed my AWS certification exam!', '2025-03-05 17:20'),
(6, 'Looking for a project partner for the DAT240 assignment.', '2025-03-06 08:50');

-- Comments
INSERT INTO comments (post_id, user_id, content, timestamp) VALUES
(1, 2, 'Welcome back Alice!', '2025-03-01 11:00'),
(2, 1, 'I’m interested Bob!', '2025-03-02 15:00'),
(3, 2, 'Nice blog Charlie!', '2025-03-03 10:00'),
(4, 1, 'I can share my notes Diana!', '2025-03-04 15:00'),
(5, 3, 'Congrats Ethan!', '2025-03-05 18:00'),
(6, 4, 'I’d love to team up!', '2025-03-06 10:00');

-- Likes
INSERT INTO likes (post_id, user_id, timestamp) VALUES
(1, 2, '2025-03-01 11:10'),
(2, 3, '2025-03-02 16:00'),
(3, 1, '2025-03-03 11:00'),
(4, 5, '2025-03-04 14:30'),
(5, 6, '2025-03-05 19:00'),
(6, 1, '2025-03-06 11:30');

-- Friendships
INSERT INTO friendships (user_id_1, user_id_2, status) VALUES
(1, 2, 'accepted'),
(1, 3, 'pending'),
(2, 3, 'accepted'),
(4, 1, 'accepted'),
(5, 6, 'accepted');
