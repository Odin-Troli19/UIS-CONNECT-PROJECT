INSERT INTO users (username, major, interests) VALUES
('Alice', 'Data Science', 'Python, AI'),
('Bob', 'Cybersecurity', 'Hacking, Networks'),
('Charlie', 'Software Engineering', 'Java, Web Dev'),
('Diana', 'Business IT', 'UX, Design Thinking'),
('Ethan', 'Cloud Computing', 'AWS, Azure'),
('Fatima', 'Machine Learning', 'Deep Learning, NLP'),
('George', 'Robotics', 'Autonomous Systems'),
('Hannah', 'Information Systems', 'Enterprise IT'),
('Isaac', 'AI & Robotics', 'Computer Vision'),
('Julia', 'Digital Forensics', 'Security Analysis');

INSERT INTO posts (user_id, content, timestamp) VALUES
(1, 'Excited to start this semester!', '2025-03-01 10:00'),
(2, 'Anyone wants to form a study group for DAT220?', '2025-03-02 10:00'),
(3, 'Check out my new blog on software design!', '2025-03-03 10:00'),
(4, 'Does anyone have notes for last lecture?', '2025-03-04 10:00'),
(5, 'I just passed my AWS certification exam!', '2025-03-05 10:00'),
(6, 'Looking for a project partner for DAT240.', '2025-03-06 10:00'),
(7, 'Studying hard for upcoming exams!', '2025-03-07 10:00'),
(8, 'Can someone help with Flask routing?', '2025-03-08 10:00'),
(9, 'This week's lecture was amazing!', '2025-03-09 10:00'),
(10, 'Let's meet for coffee and code!', '2025-03-10 10:00');

INSERT INTO comments (post_id, user_id, content, timestamp) VALUES
(1, 1, 'Great post!', '2025-03-01 11:00'),
(2, 2, 'Thanks for sharing!', '2025-03-02 11:00'),
(3, 3, 'Good luck!', '2025-03-03 11:00'),
(4, 4, 'Interesting!', '2025-03-04 11:00'),
(5, 5, 'I'll join!', '2025-03-05 11:00'),
(6, 6, 'Nice!', '2025-03-06 11:00'),
(7, 7, 'Agreed!', '2025-03-07 11:00'),
(8, 8, 'Me too!', '2025-03-08 11:00'),
(9, 9, 'Can help!', '2025-03-09 11:00'),
(10, 10, 'Same here!', '2025-03-10 11:00');

INSERT INTO likes (post_id, user_id, timestamp) VALUES
(1, 1, '2025-03-01 12:00'),
(2, 2, '2025-03-02 12:00'),
(3, 3, '2025-03-03 12:00'),
(4, 4, '2025-03-04 12:00'),
(5, 5, '2025-03-05 12:00'),
(6, 6, '2025-03-06 12:00'),
(7, 7, '2025-03-07 12:00'),
(8, 8, '2025-03-08 12:00'),
(9, 9, '2025-03-09 12:00'),
(10, 10, '2025-03-10 12:00');

INSERT INTO friendships (user_id_1, user_id_2, status) VALUES
(1, 2, 'accepted'),
(2, 3, 'accepted'),
(3, 4, 'accepted'),
(4, 5, 'accepted'),
(5, 6, 'accepted'),
(6, 7, 'accepted'),
(7, 8, 'accepted'),
(8, 9, 'accepted'),
(9, 10, 'accepted'),
(10, 1, 'accepted');

