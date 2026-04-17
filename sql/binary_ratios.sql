SELECT
    b.repo_id,
    b.repo_full_name,
    b.total_files,
    b.binary_file_count * 1.0 / b.total_files AS binary_ratio,
    b.compiled_binary_count * 1.0 / b.total_files AS compiled_binary_ratio,
    b.archive_count * 1.0 / b.total_files AS archive_ratio,
    b.has_strict_binary
FROM binary_data_summary b
JOIN (
    SELECT repo_id, MAX(scan_date) AS max_scan_date
    FROM binary_data_summary
    GROUP BY repo_id
) latest
ON b.repo_id = latest.repo_id
AND b.scan_date = latest.max_scan_date;