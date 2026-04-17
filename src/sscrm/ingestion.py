import github as gh
import repository as rp
import csv
from pathlib import Path
import json
import binary_repository as brp

from datetime import datetime, timezone

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


BASE_DIR = Path(__file__).resolve().parents[2]  # project root
CSV_PATH = BASE_DIR / "data" / "raw" / "repos_list.csv"

CHECKPOINT_FILE = Path("checkpoints.json")

CHECKPOINT_PR_FILE = Path("checkpoints2.json")

CHECKPOINT_REVIEW_FILE = Path("checkpoint_review.json")

CP_NEWEST_COMMENT = Path("cp_new_comment.json")
CP_NEWEST_REVIEW = Path("cp_new_review.json")

def load_checkpoints() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {}

def load_checkpoints_pr() -> dict:
    if CHECKPOINT_PR_FILE.exists():
        return json.loads(CHECKPOINT_PR_FILE.read_text())
    return {}

def load_checkpoints_review() -> dict:
    if CHECKPOINT_REVIEW_FILE.exists():
        return json.loads(CHECKPOINT_REVIEW_FILE.read_text())
    return {}

def load_checkpoint_newest_comment() -> dict:
    if CP_NEWEST_COMMENT.exists():
        return json.loads(CP_NEWEST_COMMENT.read_text())
    return {}

def load_checkpoint_newest_review() -> dict:
    if CP_NEWEST_REVIEW.exists():
        return json.loads(CP_NEWEST_REVIEW.read_text())
    return {}

def save_state(state: dict) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def save_state_pr(state:dict) -> None:
    CHECKPOINT_PR_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def save_state_review(state:dict) -> None:
    CHECKPOINT_REVIEW_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))

def save_state_newest_comments(state:dict) -> None:
    CP_NEWEST_COMMENT.write_text(json.dumps(state, indent=2, sort_keys=True))
   
def save_state_newest_review(state:dict) -> None:
    CP_NEWEST_REVIEW.write_text(json.dumps(state, indent=2, sort_keys=True))   

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

    rlimit = gh.rate_limit()

    while len(tpr) > 0 and rlimit >10:
        rlimit = gh.rate_limit()

        tpr = rp.get_prs_from_db(cursor_pr_id)

        for full_name, repo_id, pr_number, pr_id in tpr:
            owner = full_name.split('/')[0]
            name = full_name.split('/')[1]

            cm_json = gh.fetch_comments(owner, name, pr_number, gh.token)

            for cm in cm_json:
                try:
                    cm_object = gh.parse_comment(cm, owner, name, repo_id, pr_number)
                    rp.save_comment(cm_object)
                except Exception as e:
                    print(f"Error: {owner}, {name}, {repo_id}, {pr_number}")
                    raise e
                
            cursor_pr_id = pr_id
            progress['pr_id'] = cursor_pr_id
            save_state_pr(progress)
        print(cursor_pr_id)


def build_reviews_table():
    rp.create_reviews_table()

    progress = load_checkpoints_review()

    cursor_pr_id = progress.get('pr_id', 10000000000)

    tpr = rp.get_prs_from_db(cursor_pr_id)

    rlimit = gh.rate_limit()

    while len(tpr) > 0 and rlimit >10:
        tpr = rp.get_prs_from_db(cursor_pr_id)
        rlimit = gh.rate_limit()
        for full_name, repo_id, pr_number, pr_id in tpr:
            owner = full_name.split('/')[0]
            name = full_name.split('/')[1]

            rv_json = gh.fetch_reviews(owner, name, pr_number, gh.token)

            for rv in rv_json:
                try:
                    rv_object = gh.parse_review(rv, owner, name, repo_id, pr_number)
                    rp.save_review(rv_object)
                except Exception as e:
                    print(rlimit)
                    print(f"Error: {owner}, {name}, {repo_id}, {pr_number}")
                    raise e
                
            cursor_pr_id = pr_id
            progress['pr_id'] = cursor_pr_id
            save_state_review(progress)
        print(cursor_pr_id)


def build_comments_table_newest():
    """
    fills the table with the newest x pr comments for each repo making a broader analysis possible.
    """
    progress = load_checkpoint_newest_comment()

    if progress == {}:
        progress["offset_counter"] = 0
        progress["batchsize"] = 100
        progress["sample_start"] = 0
        progress["sample_end"] = 500



    pr_s = rp.get_newest_prs_from_db(sample_start=progress["sample_start"], sample_end=progress["sample_end"], batchsize=progress["batchsize"], offset=progress["offset_counter"])
    rlimit = gh.rate_limit()

    print(rlimit)

    while len(pr_s) > 0 and rlimit >101:
        pr_s = rp.get_newest_prs_from_db(sample_start=progress["sample_start"], sample_end=progress["sample_end"], batchsize=progress["batchsize"], offset=progress["offset_counter"])
        rlimit = gh.rate_limit()

        for full_name, repo_id, pr_number, pr_id in pr_s:
            owner = full_name.split('/')[0]
            name = full_name.split('/')[1]

            cm_json = gh.fetch_comments(owner, name, pr_number, gh.token)

            for cm in cm_json:
                try:
                    cm_object = gh.parse_comment(cm, owner, name, repo_id, pr_number)
                    rp.save_comment(cm_object)
                except Exception as e:
                    print(rlimit)
                    print(f"Error: {owner}, {name}, {repo_id}, {pr_number}")
                    raise e
        progress['offset_counter'] += progress["batchsize"]
        print(rlimit, cm_object.comment_id)
        save_state_newest_comments(progress)


def build_review_table_newest():
    progress = load_checkpoint_newest_review()

    if progress == {}:
        progress["offset_counter"] = 0
        progress["batchsize"] = 100
        progress["sample_start"] = 0
        progress["sample_end"] = 500



    pr_s = rp.get_newest_prs_from_db(sample_start=progress["sample_start"], sample_end=progress["sample_end"], batchsize=progress["batchsize"], offset=progress["offset_counter"])
    rlimit = gh.rate_limit()

    print(rlimit)

    while len(pr_s) > 0 and rlimit >101:
        pr_s = rp.get_newest_prs_from_db(sample_start=progress["sample_start"], sample_end=progress["sample_end"], batchsize=progress["batchsize"], offset=progress["offset_counter"])
        rlimit = gh.rate_limit()

        for full_name, repo_id, pr_number, pr_id in pr_s:
            owner = full_name.split('/')[0]
            name = full_name.split('/')[1]

            rv_json = gh.fetch_reviews(owner, name, pr_number, gh.token)

            for rv in rv_json:
                try:
                    rv_object = gh.parse_review(rv, owner, name, repo_id, pr_number)
                    rp.save_review(rv_object)
                except Exception as e:
                    print(rlimit)
                    print(f"Error: {owner}, {name}, {repo_id}, {pr_number}")
                    raise e
        progress['offset_counter'] += progress["batchsize"]
        print(rlimit, rv_object.review_id)
        save_state_newest_review(progress)


def build_binary_table():
    brp.create_binary_table()
    repos = rp.get_repos_from_db()
    rlimit = gh.rate_limit()

    while rlimit > 10:
        rlimit = gh.rate_limit()

        for repo_id, owner, name, full_name in repos:
            key = full_name

            binary = gh.fetch_binary(owner, name)
            binary_object = gh.parse_binary(binary["json"], owner, name, repo_id, binary["sha"], binary["default_branch"])

            brp.save_binary_data(binary_object)


if __name__ == "__main__":
    build_binary_table()
