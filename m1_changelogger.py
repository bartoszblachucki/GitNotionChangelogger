"""def install_dependencies(deps):
    def is_installed(package: str):
        import importlib
        
        try:
            importlib.import_module(package)
            return True
        except:
            return False

    def install(package: str):
        import subprocess
        
        print("pip", "install", package)
        subprocess.check_call(["pip", "install", package])
            
    for dep in deps:
        if not is_installed(dep):
            print(dep, "not installed")
            install(dep)

install_dependencies(["requests", "git", "pyperclip"])"""

# builtin
import sys
import os
import re

# pip
import git
import requests
import pyperclip

# local
import notion

def build_md_link(text: str, url: str):
    return f"[{text}]({url})"

def strip_commit_message(message: str):
    return message.split('\n', 1)[0]
    
def build_change_string(repo: git.Repo, commit: git.Commit, related_issues):
    message = strip_commit_message(commit.message)
    author = commit.author.name
    short_sha = commit.hexsha[:7]
    url = f"https://github.com/GameDev-Tube/FameMMA/commit/{commit.hexsha}"
    change_str = f"[{build_md_link(short_sha, url)}] {message} - {author}\n"

    if related_issues:
        for issue in related_issues:
            _id, url = issue
            change_str = f"[{build_md_link(_id, url)}] {change_str}"

    return "- " + change_str

def get_issue_ids_from_commit(commit: git.Commit):
    issue_id_pattern = r'ID-\d+'
    issue_ids = re.findall(issue_id_pattern, commit.message)
    return issue_ids

def get_issues_for_ids(issues, issue_ids):
    found = []
    for _id in issue_ids:
        for issue in issues:
            issue_id, issue_url = issue
            if issue_id == _id:
                found.append(issue)

    return found
    

def get_issues_for_commit(issues, commit: git.Commit):
    ids = get_issue_ids_from_commit(commit)
    if (ids):
        return get_issues_for_ids(issues, ids)

def build_changelog_for_type(commits, issues, _filter, title):

    _commits = commits
    changelog = ""

    if _filter is not None:
        _commits = [x for x in _commits if x.message.startswith(_filter)]

    if not _commits:
        return changelog

    changelog += f"{title}:\n"
    
    for commit in _commits:
        related_issues = get_issues_for_commit(issues, commit)
        changelog += build_change_string(repo, commit, related_issues)

    changelog += "\n"

    return changelog

if __name__ == "__main__":
    notion_token = sys.argv[1]
    commit_shas = sys.argv[2:]

    repo = git.Repo(".")
    commits = [repo.commit(x) for x in commit_shas]
    issues = notion.get_issues(notion_token)
    
    pretty_changelog = ""
    raw_changelog = ""

    pretty_changelog += build_changelog_for_type(commits, issues, "feat", "➕ Added")
    pretty_changelog += build_changelog_for_type(commits, issues, "fix", "🛠 Fixed")
    pretty_changelog += build_changelog_for_type(commits, issues, "perf", "🚀 Optimized")
    pretty_changelog += build_changelog_for_type(commits, issues, "refactor", "⚙️ Refactored")
    others = build_changelog_for_type(commits, issues, None, "🤷‍ Other")
    for line in others.split("\n"):
        if line not in pretty_changelog:
            pretty_changelog += line + "\n"

    raw_changelog += build_changelog_for_type(commits, issues, "feat", "Added")
    raw_changelog += build_changelog_for_type(commits, issues, "fix", "Fixed")
    raw_changelog += build_changelog_for_type(commits, issues, "perf", "Optimized")
    raw_changelog += build_changelog_for_type(commits, issues, "refactor", "Refactored")
    others = build_changelog_for_type(commits, issues, None, "Other")
    for line in others.split("\n"):
        if line not in raw_changelog:
            raw_changelog += line + "\n"
            
    pyperclip.copy(pretty_changelog)

    print()
    print(raw_changelog)
    print()
    print(f"Changelog copied to clipboard! Just paste it wherever you like. ({len(pretty_changelog)} chars)")
    print()
