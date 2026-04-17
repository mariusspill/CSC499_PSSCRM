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
    repo_id: int

    pull_request_number: str
 
    review_id: str
    reviewer_id: str
    reviewer_login: str
    reviewer_type: str

    state: str
    submitted_at: str
    is_automation: bool


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


class BinaryData:
    repo_full_name: str
    repo_id: int
    default_branch: str
    branch_sha: str

    total_items: int
    total_files: int
    total_directories: int

    binary_file_count: int
    non_binary_file_count: int

    compiled_binary_count: int
    archive_count: int
                    
    has_any_binary: bool
    has_strict_binary: bool

# Insert your token here
token = "SECRET"


def rate_limit():
    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get("https://api.github.com/rate_limit", headers=headers)
    return r.json()['resources']['core']['remaining']


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
    

def fetch_reviews(repo_owner: str, repo_name: str, pr_number: str, token:str):
    headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

    r = requests.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews', headers=headers)

    return r.json()


def parse_review(review_json:dict, repo_owner: str, repo_name: str, repo_id: int, pr_number:str) -> Review:
    result = Review()

    result.repo_owner = repo_owner
    result.repo_name = repo_name
    result.repo_full_name = f"{repo_owner}/{repo_name}"
    result.repo_id = repo_id

    result.pull_request_number = pr_number

    try:
        result.review_id = review_json['id']
    except:
        result.review_id = None
        print(review_json)

    try:
        result.reviewer_id = review_json['user']['id']
        result.reviewer_login = review_json['user']['login']
        result.reviewer_type = review_json['user']['type']
    except:
        result.reviewer_id = None
        result.reviewer_login = None
        result.reviewer_type = None
        print("Reviewer set to None")

    try:
        result.state = review_json['state']
        result.submitted_at = review_json['submitted_at']
    except:
        result.state = None
        result.submitted_at = None
        print("Review set to None")

    denylist = ['k8s-ci-robot', 
                'github-actions']

    if result.reviewer_type is not None:
        if result.reviewer_login.endswith('bot'):
            result.is_automation = True
        elif result.reviewer_login.endswith('[bot]'):
                    result.is_automation = True
        elif result.reviewer_login in denylist:
            result.is_automation = True
        elif result.reviewer_login == 'Bot':
            result.is_automation = True
        else:
            result.is_automation = False
    else:
        result.is_automation = True

    return result


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

    try:
        result.comment_id = comment_json['id']
    except:
        result.comment_id = None
        print(comment_json['id'])

    try:
        result.author_login = comment_json['user']['login']
        result.author_id = comment_json['user']['id']
        result.author_type = comment_json['user']['type']
    except:
        result.author_login = None
        result.author_id = None
        result.author_type = None
        print("author set to None")

    try:
        result.created_at = comment_json['created_at']
        result.repo_id = repo_id
    except:
        result.created_at = None
        result.repo_id = None
        print("Comments set to None")

    denylist = ['k8s-ci-robot', 
                'github-actions']

    if result.author_login.endswith('bot'):
        result.is_automation = True
    elif result.author_login.endswith('[bot]'):
        result.is_automation = True
    elif result.author_login in denylist:
        result.is_automation = True
    elif result.author_type == 'Bot':
        result.is_automation = True
    else:
        result.is_automation = False


    return result


def fetch_binary(repo_owner: str, repo_name: str):
    headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
    }

    r = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers)
    repo_data = r.json()
    default_branch = repo_data["default_branch"]

    r = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches/{default_branch}", headers=headers)
    branch_data = r.json()
    sha = branch_data["commit"]["sha"]

    r = requests.get(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{sha}?recursive=1",
        headers=headers
    )

    result = dict()
    result["default_branch"] = default_branch
    result["sha"] = sha
    result["json"] = r.json()

    return result


def parse_binary(tree_data: dict, repo_owner: str, repo_name: str, repo_id: int, sha: str, branch: str) -> BinaryData:
    result = BinaryData()
    extension_counter = dict()
    binary_counter = dict()

    result.repo_full_name = repo_owner + "/" + repo_name
    result.repo_id = repo_id
    result.branch_sha = sha
    result.default_branch = branch

    result.total_directories = 0
    result.total_files = 0

    result.non_binary_file_count = 0
    result.binary_file_count = 0

    result.compiled_binary_count = 0
    result.archive_count = 0


    BINARY_ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"}
    SUSPICIOUS_BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".jar", ".class", ".bin", ".o", ".a"}
    ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".7z", ".rar"}

    binary_counter["dangerous-binary"] = 0
    binary_counter["binary"] = 0
    binary_counter["archieve"] = 0
    binary_counter["non-binary"] = 0

    for item in tree_data["tree"]:

        if item['type'] == "blob":
            result.total_files += 1
            path = item['path'].split("/")
            filename = path[-1]
            file = filename.split('.')
            if len(file) > 1:
                extension = "." + file[-1]
            else:
                extension = None
            if extension in extension_counter.keys():
                extension_counter[extension] += 1
            else:
                extension_counter[extension] = 1

                
            if extension in BINARY_ASSET_EXTENSIONS:
                binary_counter["binary"] += 1
                result.binary_file_count += 1
            elif extension in SUSPICIOUS_BINARY_EXTENSIONS:
                binary_counter["dangerous-binary"] += 1
                result.binary_file_count += 1
                result.compiled_binary_count += 1
            elif extension in ARCHIVE_EXTENSIONS:
                binary_counter["archieve"] += 1
                result.binary_file_count += 1
                result.archive_count += 1
            else:
                binary_counter["non-binary"] += 1
                result.non_binary_file_count += 1
        else:
            result.total_directories += 1

    result.total_items = result.total_directories + result.total_files

    if binary_counter["binary"] > 0 or binary_counter["dangerous-binary"] > 0 or binary_counter["archieve"]:
        result.has_any_binary = True
    else:
        result.has_any_binary = False

    if binary_counter["dangerous-binary"] > 0:
        result.has_strict_binary = True
    else:
        result.has_strict_binary = False

    return result



if __name__ == "__main__":
    result = fetch_binary('kubernetes', 'kubernetes')
    binary = parse_binary(result["json"], 'kubernetes', 'kubernetes', 111, result['sha'], result['default_branch'])