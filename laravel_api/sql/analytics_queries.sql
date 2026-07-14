-- 1. Top 10 most active users in the last 7 days
SELECT u.id, u.name, u.email, COUNT(*) AS total_interactions
FROM users u
JOIN (
    SELECT user_id_of_post AS user_id, created_at FROM post_reactions
    UNION ALL
    SELECT current_user_id AS user_id, created_at FROM post_comments
    UNION ALL
    SELECT current_user_id AS user_id, created_at FROM post_reactions
) interactions ON interactions.user_id = u.id
WHERE interactions.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY u.id, u.name, u.email
ORDER BY total_interactions DESC
LIMIT 10;

-- 2. Posts from users a given user interacts with most, last 30 days
-- Replace :user_id with the actual user id
SELECT p.id, p.user_id AS author_id, p.text, p.created_at
FROM posts p
JOIN (
    SELECT DISTINCT current_user_id AS interacted_user_id
    FROM post_reactions
    WHERE current_user_id = :user_id
    UNION
    SELECT DISTINCT current_user_id AS interacted_user_id
    FROM post_comments
    WHERE current_user_id = :user_id
) i ON i.interacted_user_id = p.user_id
WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY p.created_at DESC;

-- 3. Posts viewed more than 100 times but with zero reactions
SELECT p.id AS post_id, p.user_id AS author_id, ps.post_views AS view_count, p.created_at
FROM posts p
JOIN post_scores ps ON ps.post_id = p.id
LEFT JOIN post_reactions pr ON pr.post_id = p.id
WHERE ps.post_views > 100
GROUP BY p.id, p.user_id, ps.post_views, p.created_at
HAVING COUNT(pr.id) = 0;

-- 4. Potential spam: users who created more than 20 posts in the last 24 hours
SELECT u.id, u.email, COUNT(p.id) AS post_count
FROM users u
JOIN posts p ON p.user_id = u.id
WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY u.id, u.email
HAVING COUNT(p.id) > 20;
