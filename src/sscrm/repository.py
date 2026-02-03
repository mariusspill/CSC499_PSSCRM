import sqlite3
from pathlib import Path
from github import PullRequest

DB_PATH = 'sscrm.sqlite'

def create_pull_requests_table():

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute("""
    CREATE TABLE IF NOT EXISTS pull_requests(
                    repo_full_name  TEXT NOT NULL,
                    pr_number INTEGER NOT NULL,
                    pr_id INTEGER,

                    created_at TEXT,
                    updated_at TEXT,
                    closed_at TEXT,
                    merged_at TEXT,

                    author_id INTEGER,
                    author_username TEXT,
                    author_type TEXT,

                    state TEXT,
                    draft INTEGER,

                    base_ref TEXT,
                    merged_by_login TEXT,

                    PRIMARY KEY (repo_full_name, pr_number)
                    );
                    """)
    
        conn.commit()


def save_pr(pr: PullRequest):
        
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute("""
INSERT INTO pull_requests (repo_full_name,
                    pr_number, pr_id, created_at, updated_at, closed_at, merged_at,
                    author_id, author_username, author_type,
                    state, draft, base_ref, merged_by_login)
                    
                    
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) 
                    
                    ON CONFLICT(repo_full_name, pr_number) DO NOTHING
                """, (pr.repo_full_name, pr.number, pr.id, pr.created_at, pr.updated_at, pr.closed_at, pr.merged_at,
                      pr.author_id, pr.author_username, pr.author_usertype, pr.state, pr.draft, pr.base_ref, pr.merged_by_login))
        
        conn.commit()