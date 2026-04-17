WITH participants AS (
    SELECT
        repo_id,
        pr_number,
        reviewer_login AS user_login
    FROM reviews
    WHERE is_automation = 0
      AND LOWER(reviewer_login) NOT IN (
          'cockroach-teamcity',
          'github-actions',
          'github-actions[bot]',
          'dependabot',
          'dependabot[bot]',
          'renovate',
          'renovate[bot]',
          'codecov',
          'codecov[bot]',
          'travis-ci',
          'travis-ci[bot]',
          'circleci',
          'circleci[bot]',
          'azure-pipelines',
          'azure-pipelines[bot]',
          'buildkite',
          'buildkite[bot]',
          'jenkins',
          'jenkinsci',
          'teamcity',
          'netlify',
          'netlify[bot]',
          'mergify',
          'mergify[bot]',
          'semantic-release-bot',
          'imgbot',
          'imgbot[bot]',
          'snyk-bot',
          'snyk-bot[bot]'
      )

    UNION

    SELECT
        repo_id,
        pr_number,
        author_login AS user_login
    FROM comments
    WHERE is_automation = 0
      AND LOWER(author_login) NOT IN (
          'cockroach-teamcity',
          'github-actions',
          'github-actions[bot]',
          'dependabot',
          'dependabot[bot]',
          'renovate',
          'renovate[bot]',
          'codecov',
          'codecov[bot]',
          'travis-ci',
          'travis-ci[bot]',
          'circleci',
          'circleci[bot]',
          'azure-pipelines',
          'azure-pipelines[bot]',
          'buildkite',
          'buildkite[bot]',
          'jenkins',
          'jenkinsci',
          'teamcity',
          'netlify',
          'netlify[bot]',
          'mergify',
          'mergify[bot]',
          'semantic-release-bot',
          'imgbot',
          'imgbot[bot]',
          'snyk-bot',
          'snyk-bot[bot]'
      )
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
),

review_metrics AS (
    SELECT
        repo_id,
        COUNT(*) AS observed_prs,
        SUM(is_multi_party) AS multi_party_prs,
        SUM(is_multi_party) * 1.0 / COUNT(*) AS multi_party_rate
    FROM flags
    GROUP BY repo_id
),

pr_counts AS (
    SELECT
        repo_id,
        COUNT(*) AS pr_count
    FROM pull_requests
    GROUP BY repo_id
)

SELECT
    r.id AS repo_id,
    r.full_name AS repo_full_name,
    p.pr_count,
    m.observed_prs,
    m.multi_party_prs,
    ROUND(m.observed_prs * 1.0 / p.pr_count, 3) AS coverage_rate,
    ROUND(m.multi_party_rate, 3) AS multi_party_rate
FROM repositories r
JOIN review_metrics m
    ON r.id = m.repo_id
JOIN pr_counts p
    ON r.id = p.repo_id
ORDER BY m.multi_party_rate DESC;