import sqlite3
from pathlib import Path
from github import PullRequest
from github import Repository
from github import Comment
from github import Review
import github as gh

DB_PATH = 'sscrm.sqlite'


def create_repository_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS repositories(
                    id INTEGER PRIMARY KEY,
                    owner TEXT NOT NULL,
                    name TEXT NOT NULL,
                    full_name TEXT NOT NULL UNIQUE,

                    created_at TEXT,
                    
                    stars INTEGER,
                    size INTEGER,
                    forks INTEGER,
                    open_issues INTEGER
                    );
                    """)
        
        conn.commit()

def save_repository(repo: Repository):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
INSERT INTO repositories (id, owner, name, full_name, created_at,
                    stars, size, forks, open_issues)
                    
                    
                    VALUES (?,?,?,?,?,?,?,?,?)
                    
                    ON CONFLICT(full_name) DO NOTHING
                """, (repo.id, repo.owner, repo.name, repo.full_name, repo.created_at,
                      repo.stars, repo.size, repo.forks, repo.open_issues))

        conn.commit()



def create_pull_requests_table():

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")


        cur.execute("""
    CREATE TABLE IF NOT EXISTS pull_requests(
                    repo_full_name  TEXT NOT NULL,
                    repo_id INTEGER NOT NULL,
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

                    PRIMARY KEY (repo_id, pr_number),
                    FOREIGN KEY (repo_id) REFERENCES repositories(id)
                    );
                    """)
    
        conn.commit()


def save_pr(pr: PullRequest):
        
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")
   

        cur.execute("""
INSERT INTO pull_requests (repo_full_name, repo_id,
                    pr_number, pr_id, created_at, updated_at, closed_at, merged_at,
                    author_id, author_username, author_type,
                    state, draft, base_ref, merged_by_login)
                    
                    
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) 
                    
                    ON CONFLICT(repo_id, pr_number) DO UPDATE SET
                        updated_at = excluded.updated_at,
                        closed_at = excluded.closed_at,
                        merged_at = excluded.merged_at,
                        state = excluded.state,
                        draft = excluded.draft,
                        merged_by_login = excluded.merged_by_login
                """, (pr.repo_full_name,pr.repo_id, pr.number, pr.id, pr.created_at, pr.updated_at, pr.closed_at, pr.merged_at,
                      pr.author_id, pr.author_username, pr.author_usertype, pr.state, pr.draft, pr.base_ref, pr.merged_by_login))
        
        conn.commit()


def create_comments_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments(
                    comment_id INTEGER PRIMARY KEY,
                    repo_owner TEXT,
                    repo_name TEXT,
                    repo_id INTEGER NOT NULL,
                    pr_number INTEGER NOT NULL,
                    author_login TEXT,
                    author_id INTEGER,
                    author_type TEXT,
                    created_at TEXT,
                    is_automation INTEGER,

                    FOREIGN KEY (repo_id) REFERENCES repositories(id),
                    FOREIGN KEY (repo_id, pr_number) REFERENCES pull_requests(repo_id, pr_number)
                    );
""")

        conn.commit()

def save_comment(cm: Comment):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
INSERT INTO comments (
                    repo_owner, repo_name, repo_id, pr_number, comment_id, author_login, 
                    author_id, author_type, created_at, is_automation)
                    
                    VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(comment_id) DO NOTHING;
                        """, (cm.repo_owner, cm.repo_name, cm.repo_id, cm.pr_number, cm.comment_id, cm.author_login,
                              cm.author_id, cm.author_type, cm.created_at, cm.is_automation))
        
        conn.commit()


def create_reviews_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews(
                    review_id INTEGER PRIMARY KEY,
                    repo_owner TEXT,
                    repo_name TEXT,
                    repo_id INTEGER NOT NULL,
                    pr_number INTEGER NOT NULL,
                    reviewer_login TEXT,
                    reviewer_id INTEGER,
                    reviewer_type TEXT,
                    state TEXT,
                    submitted_at TEXT,
                    is_automation INTEGER,

                    FOREIGN KEY (repo_id) REFERENCES repositories(id),
                    FOREIGN KEY (repo_id, pr_number) REFERENCES pull_requests(repo_id, pr_number)
                    );
""")

        conn.commit()


def save_review(rv: Review):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
INSERT INTO reviews (
                    review_id, repo_owner, repo_name, repo_id, pr_number, reviewer_login, reviewer_id, 
                    reviewer_type, state, submitted_at, is_automation)
                    
                    VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(comment_id) DO NOTHING;
                        """, (rv.review_id, rv.repo_owner, rv.repo_name, rv.repo_id, rv.pull_request_number,
                              rv.reviewer_login, rv.reviewer_id, rv.reviewer_type, rv.state, rv.submitted_at, rv.is_automation))
        
        conn.commit()


def get_repos_from_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON;")

        cur.execute("""
                SELECT id, owner, name, full_name FROM repositories
                    """)
        
        return cur.fetchall()
    

def get_prs_from_db(cursor: int=10000000000):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute(f"""
            SELECT repo_full_name, repo_id, pr_number, pr_id  FROM pull_requests WHERE pr_id < {cursor}  ORDER BY pr_id DESC LIMIT 100;
""")

        conn.execute("PRAGMA foreign_keys = ON;")

        return cur.fetchall()
    

if __name__ == "__main__":
    cm = gh.debug()
    print(cm.repo_id, cm.pr_number)
    save_comment(cm)