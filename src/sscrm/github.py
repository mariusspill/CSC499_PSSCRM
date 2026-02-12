import requests
import json


class Repository:
    id: int
    owner: str
    name: str
    full_name: str

    created_at: str

    size: int
    forks: int
    open_issues: int
    stars: int

class PullRequest:
    repo_owner: str
    repo_name: str
    repo_full_name: str
    repo_id: int
    number: str
    id: str
    created_at: str
    updated_at: str
    closed_at: str
    merged_at: str
    author_id: str
    author_username: str
    author_usertype: str
    state: str
    draft: bool
    base_ref: str
    merged_by_login: str

class Review:
    repo_owner: str
    repo_name: str
    repo_full_name: str
    pull_request_id: str
    pull_request_number: str
    review_id: str
    reviewer_id: str
    reviewer_login: str
    state: str
    submitted_at: str

class Comment:
    repo_owner: str
    repo_name: str
    repo_full_name: str
    repo_id: int
    pr_number: str
    comment_id: int
    author_login: str
    author_id: int
    author_type: int
    created_at: str
    is_automation: bool


token = "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"


def fetch_repo(repo_owner: str, repo_name: str, token: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    r = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers)

    return r.json()


def parse_repo(repo_json: dict, repo_owner: str, repo_name: str) -> Repository:
    result = Repository()

    result.owner = repo_owner
    result.name = repo_name
    result.full_name = f"{repo_owner}/{repo_name}"

    result.id = repo_json['id']
    result.created_at = repo_json['created_at']
    result.stars = repo_json['watchers']
    result.size = repo_json['size']
    result.forks = repo_json['forks']
    result.open_issues = repo_json['open_issues']

    return result


def parse_pull_request(pr_json:dict, repo_owner:str, repo_name:str, repo_id:int) -> PullRequest:
    result = PullRequest()

    result.repo_owner = repo_owner
    result.repo_name = repo_name
    result.repo_full_name = f'{repo_owner}/{repo_name}'
    result.repo_id = repo_id

    result.number = pr_json['number']
    result.id = pr_json['id']

    result.created_at = pr_json['created_at']
    result.updated_at = pr_json['updated_at']
    result.closed_at = pr_json['closed_at']
    result.merged_at = pr_json['merged_at']

    result.author_id = pr_json['user']['id']
    result.author_username = pr_json['user']['login']
    result.author_usertype = pr_json['user']['type']

    result.state = pr_json['state']
    result.draft = pr_json['draft']
    result.base_ref = pr_json['base']['ref']
    result.merged_by_login = ''

    return result


def fetch_pull_requests(repo_owner:str, repo_name:str, token:str,
                        state: str = "closed",
                        per_page: int = 1,
                        sort: str = 'created',
                        direction: str = 'asc',
                        page: int = 1):
    params = {
        "state": state,
        "per_page": per_page,
        "sort": sort,
        "direction": direction,
        "page": page
    }

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    r = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls', headers=headers, params=params)
    print(r.headers.get("X-RateLimit-Remaining"))


    try:
        return r.json()
    except:
        return None


def parse_review(review_json:dict, repo_owner: str, repo_name:str, pr_number:str, pr_id:str) -> Review:
    result = Review()

    result.repo_owner = repo_owner
    result.repo_name = repo_name
    result.repo_full_name = f"{repo_owner}/{repo_name}"

    result.pull_request_id = pr_id
    result.pull_request_number = pr_number

    result.review_id = review_json['id']
    result.reviewer_id = review_json['user']['id']
    result.reviewer_login = review_json['user']['login']

    result.state = review_json['state']
    result.submitted_at = review_json['submitted_at']

    return result


def fetch_reviews(repo_owner: str, repo_name: str, pr_number: str, token:str):
    headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

    r = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews', headers=headers)

    return r.json()


def fetch_comments(repo_owner: str, repo_name: str, pr_number: str, token: str):
    headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }
    
    r = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments', headers=headers)

    return r.json()



def parse_comment(comment_json: dict, repo_owner: str, repo_name: str, repo_id:int, pr_number: str) -> Comment:
    result = Comment()

    result.repo_owner = repo_owner
    result.repo_name = repo_name
    result.repo_full_name = f"{repo_owner}/{repo_name}"

    result.pr_number = pr_number

    result.comment_id = comment_json['id']

    result.author_login = comment_json['user']['login']
    result.author_id = comment_json['user']['id']
    result.author_type = comment_json['user']['type']

    result.created_at = comment_json['created_at']
    result.repo_id = repo_id

    denylist = ['k8s-ci-robot', 
                'github-actions']

    if result.author_login.endswith('bot'):
        result.is_automation = True
    elif result.author_login in denylist:
        result.is_automation = True
    elif result.author_type == 'Bot':
        result.is_automation = True
    else:
        result.is_automation = False


    return result


def debug():
    data = fetch_comments('cockroachdb', 'cockroach', 163371, token)
    cm = parse_comment(data[0], 'cockroachdb', 'cockroach', 16563587, 163371)
    print(cm.is_automation)

if __name__ == "__main__":
    debug()