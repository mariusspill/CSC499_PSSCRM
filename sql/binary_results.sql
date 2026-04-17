DROP VIEW IF EXISTS binary_results;

CREATE VIEW binary_results AS
SELECT
    b.repo_id,
    b.repo_full_name,
    b.total_files,
    ROUND(b.binary_file_count * 1.0 / b.total_files, 3) AS binary_ratio,
    ROUND(b.compiled_binary_count * 1.0 / b.total_files, 3) AS compiled_binary_ratio,
    ROUND(b.archive_count * 1.0 / b.total_files, 3) AS archive_ratio,
    b.has_strict_binary
FROM binary_data_summary b
JOIN (
    SELECT
        repo_id,
        MAX(scan_date) AS max_scan_date
    FROM binary_data_summary
    GROUP BY repo_id
) latest
    ON b.repo_id = latest.repo_id
   AND b.scan_date = latest.max_scan_date
ORDER BY binary_ratio DESC;

SELECT * FROM binary_results;