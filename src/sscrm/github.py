import requests
import json

class PullRequest:
    repo_owner: str
    repo_name: str
    repo_full_name: str
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



token = "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"


def parse_pull_request(pr_json:dict, repo_owner:str, repo_name:str) -> PullRequest:
    result = PullRequest()

    result.repo_owner = repo_owner
    result.repo_name = repo_name
    result.repo_full_name = f'{repo_owner}/{repo_name}'

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
                        page: int = 1):
    params = {
        "state": state,
        "per_page": per_page,
        "page": page
    }

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    r = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls', headers=headers, params=params)
    print(r.headers.get("X-RateLimit-Remaining"))

    return r.json()

data = fetch_pull_requests('kubernetes','kubernetes', token)
data = data[0]

test2 = parse_pull_request(data,'kubernetes','kubernetes')


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


def fetch_reviews(repo_owner: str, repo_name: str, pr_number: str, pr_id: str, token:str):
    headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

    r = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews', headers=headers)

    return r.json()

