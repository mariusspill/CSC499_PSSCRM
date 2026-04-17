import sqlite3
from pathlib import Path
from github import BinaryData
import github as gh

from datetime import datetime, timezone



DB_PATH = 'sscrm.sqlite'


def create_binary_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS binary_data_summary(
                    repo_full_name  TEXT NOT NULL,
                    repo_id INTEGER NOT NULL,
                    default_branch TEXT NOT NULL,
                    branch_sha TEXT NOT NULL,

                    scan_date TEXT NOT NULL,

                    
                    total_items INTEGER NOT NULL,
                    total_files INTEGER NOT NULL,
                    total_directories INTEGER NOT NULL,


                    binary_file_count INTEGER NOT NULL,
                    non_binary_file_count INTEGER NOT NULL,

                    compiled_binary_count INTEGER NOT NULL DEFAULT 0,
                    archive_count INTEGER NOT NULL DEFAULT 0,
                    
                    has_any_binary INTEGER NOT NULL,
                    has_strict_binary INTEGER NOT NULL,

                    
                    PRIMARY KEY (repo_id, branch_sha),
                    FOREIGN KEY (repo_id) REFERENCES repositories(id)
                    )""")
        

        conn.commit()

def save_binary_data(binary: BinaryData):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        now = now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute(""" INSERT INTO binary_data_summary (repo_full_name, repo_id, default_branch, branch_sha, scan_date,
                    total_items, total_files, total_directories, binary_file_count, non_binary_file_count, compiled_binary_count, archive_count,
                    has_any_binary, has_strict_binary ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    
                    ON CONFLICT(repo_id, branch_sha) DO NOTHING
                    """, (binary.repo_full_name, binary.repo_id, binary.default_branch, binary.branch_sha, now, binary.total_items,
                          binary.total_files, binary.total_directories, binary.binary_file_count, binary.non_binary_file_count, binary.compiled_binary_count, binary.archive_count,
                          binary.has_any_binary, binary.has_strict_binary))

        conn.commit()
