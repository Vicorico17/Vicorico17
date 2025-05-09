import os
import requests
import datetime
import re

USERNAME = os.environ.get('GITHUB_USERNAME')
TOKEN = os.environ.get('GITHUB_TOKEN')
README_PATH = 'README.md'

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def get_repos(username):
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{username}/repos?per_page=100&page={page}'
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_commit_count(username, repo, since=None):
    count = 0
    page = 1
    while True:
        url = f'https://api.github.com/repos/{username}/{repo}/commits?author={username}&per_page=100&page={page}'
        if since:
            url += f'&since={since}'
        r = requests.get(url, headers=headers)
        data = r.json()
        if not isinstance(data, list) or not data:
            break
        count += len(data)
        page += 1
    return count

def main():
    repos = get_repos(USERNAME)
    total_commits = 0
    this_year_commits = 0
    this_year = datetime.datetime.now().year
    since = f"{this_year}-01-01T00:00:00Z"
    for repo in repos:
        repo_name = repo['name']
        total_commits += get_commit_count(USERNAME, repo_name)
        this_year_commits += get_commit_count(USERNAME, repo_name, since=since)
    # Update README
    with open(README_PATH, 'r') as f:
        content = f.read()
    content = re.sub(r'\*\*Total commits:\*\* [0-9]+', f'**Total commits:** {total_commits}', content)
    content = re.sub(r'\*\*Commits this year:\*\* [0-9]+', f'**Commits this year:** {this_year_commits}', content)
    with open(README_PATH, 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main() 