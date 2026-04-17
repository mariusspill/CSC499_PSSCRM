import requests
import github as gh

url = "https://api.github.com/search/repositories"

query = (
    "language:Python "
    "language:C++ "
    "language:Go "
    "language:Java "
    "language:JavaScript "
    "language:PHP "
    "language:Ruby "
    "language:Rust "
    "language:C "
    "language:C# "
    "language:Swift "
    "stars:>200000 "
    "mirror:false "
    "archived:false "
    "NOT -awesome "
    "NOT -list "
    "NOT -learn "
    "NOT -algorithms "
    "NOT -books"
)

params = {
    "q": query,
    "per_page": 100,
    "page": 1
}

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"Bearer {gh.token}"
}

response = requests.get(url, headers=headers, params=params)
response.raise_for_status()

data = response.json()
print(data['items'][1])
