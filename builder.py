import re
import git
import notion


def build_md_link(text: str, url: str):
    return f"[{text}]({url})"


def strip_commit_message(message: str):
    return message.split('\n', 1)[0]


def extract_type_from_commit_message(message: str):
    pattern = r'^\s*([a-zA-Z]+)\s*(\!)?'
    match = re.match(pattern, message)

    if match:
        return match.group(1), match.group(2) == '!'
    else:
        return None, False


def is_breaking_change(commit):
    _, is_exclamation = extract_type_from_commit_message(commit.message)
    return is_exclamation


def build_commit_url(repo: git.Repo, commit: git.Commit):
    if not repo.remotes:
        return None

    remote_url = repo.remotes[0].url
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]

    url = f"{remote_url}/commit/{commit.hexsha}"
    return url


def build_change_string(repo: git.Repo, commit: git.Commit, related_issues):
    message = strip_commit_message(commit.message)
    author = commit.author.email
    short_sha = commit.hexsha[:7]

    raw_change = f"{message} - {author}"
    pretty_change = f"{message} - {author}"

    if repo.remotes:
        remote_url = repo.remotes[0].url
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]

        url = f"{remote_url}/commit/{commit.hexsha}"
        md_url = build_md_link(short_sha, url)
        raw_change = f"[{md_url}] {raw_change}"
        pretty_change = f"[{md_url}] {pretty_change}"

    if related_issues:
        for issue in related_issues:
            _id, url = issue
            md_issue = build_md_link(_id, url)
            raw_change = f"[{md_issue}] {raw_change}"
            pretty_change = f"[{md_issue}] {pretty_change}"

    if is_breaking_change(commit):
        raw_change = f"BREAKING CHANGE: {raw_change}"
        pretty_change = f"⚠️**BREAKING CHANGE:**⚠️ {pretty_change}"

    return "- " + raw_change + "\n", "- " + pretty_change + "\n"


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
    if ids:
        return get_issues_for_ids(issues, ids)


def build_type_changelog(repo, _commits, issues, commit_type):
    raw_changelog = f"{commit_type.changelog_title}:\n"
    pretty_changelog = f"{commit_type.emoji} {commit_type.changelog_title}:\n"

    for commit in _commits:
        related_issues = get_issues_for_commit(issues, commit)
        raw_change, pretty_change = build_change_string(repo, commit, related_issues)
        raw_changelog += raw_change
        pretty_changelog += pretty_change

    raw_changelog += "\n"
    pretty_changelog += "\n"

    return raw_changelog, pretty_changelog


class CommitType:
    def __init__(self, prefix, changelog_title, emoji):
        self.prefix = prefix
        self.changelog_title = changelog_title
        self.emoji = emoji


commit_types = [
    CommitType("feat", "Added", "✅"),
    CommitType("fix", "Fixed", "🛠"),
    CommitType("deprecate", "Deprecated", "👴"),
    CommitType("chore", "Maintained", "🧹"),
    CommitType("refactor", "Refactored", "🔨"),
    CommitType("style", "Styled", "🎨"),
    CommitType("test", "Tested", "🧪"),
    CommitType("perf", "Optimized", "🚀"),
    CommitType("docs", "Documented", "📝"),
    CommitType("remove", "Removed", "❌"),
]

other_commit_type = CommitType(None, "Other", "📦")


def build_changelog(notion_token, repo_directory, commit_shas) -> tuple:
    repo = git.Repo(repo_directory)
    commits = [repo.commit(x) for x in commit_shas]
    issues = notion.get_issues(notion_token)

    commits_by_type = {}
    for commit_type in commit_types:
        commits_by_type[commit_type] = []
    commits_by_type[other_commit_type] = []

    for commit in commits:
        for commit_type in commit_types:
            if commit.message.startswith(commit_type.prefix):
                commits_by_type[commit_type].append(commit)
                break
        else:
            commits_by_type[other_commit_type].append(commit)

    raw_changelog = ""
    pretty_changelog = ""

    for commit_type in commit_types + [other_commit_type]:
        _commits = commits_by_type[commit_type]
        if _commits:
            raw_type_changelog, pretty_type_changelog = build_type_changelog(repo, _commits, issues, commit_type)
            raw_changelog += raw_type_changelog
            pretty_changelog += pretty_type_changelog

    return raw_changelog, pretty_changelog


def get_commit_url(repo_directory, commit_sha):
    repo = git.Repo(repo_directory)
    commit = repo.commit(commit_sha)
    url = build_commit_url(repo, commit)
    return url
