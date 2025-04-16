-- Users
INSERT INTO users (username, major, interests) VALUES
('Alice', 'Data Science', 'AI, Python'),
('Bob', 'Cybersecurity', 'Hacking, Networks'),
('Charlie', 'Software Engineering', 'Java, Web Dev');

-- Posts
INSERT INTO posts (user_id, content, timestamp) VALUES
(1, 'Excited to start this semester!', '2025-03-01 10:00'),
(2, 'Anyone wants to form a study group for DAT220?', '2025-03-02 14:30'),
(3, 'Check out my new blog on software design!', '2025-03-03 09:15');

-- Comments
INSERT INTO comments (post_id, user_id, content, timestamp) VALUES
(1, 2, 'Welcome back Alice!', '2025-03-01 11:00'),
(2, 1, 'I’m interested Bob!', '2025-03-02 15:00'),
(3, 2, 'Nice blog Charlie!', '2025-03-03 10:00');

-- Likes
INSERT INTO likes (post_id, user_id, timestamp) VALUES
(1, 2, '2025-03-01 11:10'),
(2, 3, '2025-03-02 16:00'),
(3, 1, '2025-03-03 11:00');

-- Friendships
INSERT INTO friendships (user_id_1, user_id_2, status) VALUES
(1, 2, 'accepted'),
(1, 3, 'pending'),
(2, 3, 'accepted');
