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

# pip
import pyperclip

# local
import builder


if __name__ == "__main__":
    notion_token = sys.argv[1]
    repo_directory = sys.argv[2]
    commit_shas = sys.argv[3:]

    raw_changelog, pretty_changelog = builder.build_changelog(notion_token, repo_directory, commit_shas)

    pyperclip.copy(pretty_changelog)

    print()
    print(raw_changelog)
    print()
    print(f"Changelog copied to clipboard! Just paste it wherever you like. ({len(pretty_changelog)} chars)")
    print()
