WITH participants AS (
    SELECT
        repo_id,
        pr_number,
        reviewer_login AS user_login
    FROM reviews
    WHERE is_automation = 0

    UNION

    SELECT
        repo_id,
        pr_number,
        author_login AS user_login
    FROM comments
    WHERE is_automation = 0
),

filtered AS (
    SELECT
        p.repo_id,
        p.pr_number,
        p.user_login
    FROM participants p
    JOIN pull_requests pr
        ON p.repo_id = pr.repo_id
       AND p.pr_number = pr.pr_number
    WHERE p.user_login != pr.author_username
),

counts AS (
    SELECT
        repo_id,
        pr_number,
        COUNT(DISTINCT user_login) AS participant_count
    FROM filtered
    GROUP BY repo_id, pr_number
),

observed_prs AS (
    SELECT repo_id, pr_number FROM reviews
    UNION
    SELECT repo_id, pr_number FROM comments
),

flags AS (
    SELECT
        o.repo_id,
        o.pr_number,
        CASE
            WHEN COALESCE(c.participant_count, 0) >= 2 THEN 1
            ELSE 0
        END AS is_multi_party
    FROM observed_prs o
    LEFT JOIN counts c
        ON o.repo_id = c.repo_id
       AND o.pr_number = c.pr_number
)

SELECT
    repo_id,
    COUNT(*) AS observed_prs,
    SUM(is_multi_party) AS multi_party_prs,
    SUM(is_multi_party) * 1.0 / COUNT(*) AS multi_party_rate
FROM flags
GROUP BY repo_id;