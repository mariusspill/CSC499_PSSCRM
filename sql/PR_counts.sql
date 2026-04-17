SELECT
    repo_id,
    COUNT(*) AS pr_count
FROM pull_requests
GROUP BY repo_id;