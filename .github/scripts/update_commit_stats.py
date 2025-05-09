import os
import requests
import datetime
import re
import time

USERNAME = os.environ.get('GITHUB_USERNAME')
TOKEN = os.environ.get('GITHUB_TOKEN')
README_PATH = 'README.md'
ORG_NAME = 'arkadia-park'

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def get_repos_for_user(username):
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

def get_repos_for_org(org):
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/orgs/{org}/repos?per_page=100&page={page}'
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_commit_stats(repo_full_name, since_year=None):
    url = f'https://api.github.com/repos/{repo_full_name}/stats/contributors'
    for _ in range(10):  # Retry up to 10 times if GitHub is generating stats
        r = requests.get(url, headers=headers)
        if r.status_code == 202:
            time.sleep(2)  # Wait for GitHub to generate stats
            continue
        data = r.json()
        if not isinstance(data, list):
            return 0, 0
        total = 0
        this_year = 0
        current_year = datetime.datetime.now().year
        for contributor in data:
            for week in contributor.get('weeks', []):
                week_date = datetime.datetime.utcfromtimestamp(week['w'])
                total += week['c']
                if since_year and week_date.year == since_year:
                    this_year += week['c']
        return total, this_year
    return 0, 0

def main():
    user_repos = get_repos_for_user(USERNAME)
    org_repos = get_repos_for_org(ORG_NAME)
    all_repos = user_repos + org_repos
    total_commits = 0
    this_year_commits = 0
    this_year = datetime.datetime.now().year
    for repo in all_repos:
        repo_full_name = repo['full_name']
        repo_total, repo_this_year = get_commit_stats(repo_full_name, since_year=this_year)
        total_commits += repo_total
        this_year_commits += repo_this_year
    # Update README
    with open(README_PATH, 'r') as f:
        content = f.read()
    content = re.sub(r'\*\*Total commits:\*\* [0-9]+', f'**Total commits:** {total_commits}', content)
    content = re.sub(r'\*\*Commits this year:\*\* [0-9]+', f'**Commits this year:** {this_year_commits}', content)
    with open(README_PATH, 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main() 