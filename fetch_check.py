import json, urllib.request, urllib.error, sys

with open('repos.json', 'r') as f:
    data = json.load(f)
repos = data.get('value', [])
issues = []
for repo in repos:
    owner = repo['owner']['login']
    name = repo['name']
    raw_url = f'https://raw.githubusercontent.com/{owner}/{name}/main/SKILL.md'
    try:
        with urllib.request.urlopen(raw_url) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
        first_line = content.splitlines()[0].strip() if content else ''
        if not first_line.startswith('---'):
            issues.append(f"{owner}/{name}: missing or malformed front‑matter (first line: '{first_line}')")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            issues.append(f"{owner}/{name}: SKILL.md not found")
        else:
            issues.append(f"{owner}/{name}: HTTP error {e.code}")
    except Exception as e:
        issues.append(f"{owner}/{name}: error {e}")

print('\n'.join(issues))
