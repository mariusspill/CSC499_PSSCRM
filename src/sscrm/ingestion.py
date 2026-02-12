import github as gh
import repository as rp
import csv
from pathlib import Path
import json

from datetime import datetime, timezone

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


BASE_DIR = Path(__file__).resolve().parents[2]  # project root
CSV_PATH = BASE_DIR / "data" / "raw" / "repos_list.csv"

CHECKPOINT_FILE = Path("checkpoints.json")

CHECKPOINT_PR_FILE = Path("checkpoints2.json")

def load_checkpoints() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {}

def load_checkpoints_pr() -> dict:
    if CHECKPOINT_PR_FILE.exists():
        return json.loads(CHECKPOINT_PR_FILE.read_text())
    return {}

def save_state(state: dict) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def save_state_pr(state:dict) -> None:
    CHECKPOINT_PR_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def build_repo_table():
    rp.create_repository_table()

    with open(CSV_PATH, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            owner = row['owner']
            name = row['name']
            data = gh.fetch_repo(owner, name, gh.token)
            repo = gh.parse_repo(data, owner, name)

            rp.save_repository(repo)


def build_pr_table():
    rp.create_pull_requests_table()

    repos = rp.get_repos_from_db()
    progress = load_checkpoints()

    for repo_id, owner, name, full_name in repos:
        key = full_name

        if key in progress:
            page = progress[key].get('backfill_page', 1)
            completed = progress[key].get('completed', False)
            updated = progress[key].get("last_updated", None)
            pr_number = progress[key].get("last_pr_number", None)
        else:
            page = 1
            completed = False
            updated = None
            pr_number = None

        progress[key] = {"backfill_page": page, "completed": completed, "last_updated": updated, "last_pr_number": pr_number}
        save_state(progress)


        if completed:
            continue

        while completed == False:
            prs_json = gh.fetch_pull_requests(owner, name, gh.token, state='all', sort='created', direction='desc', per_page=100, page=page)
            
            if prs_json == None:
                progress[key] = {"backfill_page": page, "completed": completed, "last_updated": updated, "last_pr_number": pr_number}
                save_state(progress)
                continue

            if len(prs_json) == 0:
                completed = True
                progress[key] = {"backfill_page": page, "completed": completed, "last_updated": updated, "last_pr_number": pr_number}
                save_state(progress)
                continue

            for pr in prs_json:
                try:
                    pr_object = gh.parse_pull_request(pr, owner, name, repo_id)
                    rp.save_pr(pr_object)
                except Exception as e:
                    print(f"ERROR saving {full_name} pr={pr.get('number')} : {e}")

            
            page += 1
            progress[key] = {"backfill_page": page, "completed": completed, "last_updated": updated, "last_pr_number": pr_number}


            save_state(progress)


def build_comments_table():
    rp.create_comments_table()

    progress = load_checkpoints_pr()

    cursor_pr_id = progress.get('pr_id', 10000000000)

    tpr = rp.get_prs_from_db(cursor_pr_id)


    while len(tpr) > 0:
        tpr = rp.get_prs_from_db(cursor_pr_id)

        for full_name, repo_id, pr_number, pr_id in tpr:
            owner = full_name.split('/')[0]
            name = full_name.split('/')[1]

            cm_json = gh.fetch_comments(owner, name, pr_number, gh.token)

            for cm in cm_json:
                try:
                    cm_object = gh.parse_comment(cm, owner, name, repo_id, pr_number)
                    rp.save_comment(cm_object)
                except:
                    print(f"Error: {owner}, {name}, {repo_id}, {pr_number}")
                
            cursor_pr_id = pr_id
            progress['pr_id'] = cursor_pr_id
            save_state_pr(progress)
        print(cursor_pr_id)


def build_reviews_table():
    pass

if __name__ == "__main__":
    build_comments_table()