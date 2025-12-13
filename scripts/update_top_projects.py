import urllib.request
import json
import re
import os

USERNAME = "JacobZhuu"
README_PATH = "README.md"
MARKER_START = "<!-- TOP_PROJECTS_START -->"
MARKER_END = "<!-- TOP_PROJECTS_END -->"

# Configuration
# MODE can be "AUTO" or "STATIC"
MODE = "STATIC" 

# List of repository names for STATIC mode
STATIC_PROJECTS = [
    "GLoCIM-Simple",
    "link-prediction"
]

def get_top_repos():
    if MODE == "STATIC":
        print(f"Running in STATIC mode. Selected projects: {STATIC_PROJECTS}")
        return [{"name": name} for name in STATIC_PROJECTS]

    print("Running in AUTO mode.")
    url = f"https://api.github.com/users/{USERNAME}/repos?type=owner&sort=stars&direction=desc&per_page=100"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            repos = json.loads(data)
            
            # Filter for public repos
            public_repos = [
                r for r in repos 
                if not r.get("private") 
                and r["name"].lower() != USERNAME.lower()
                and r.get("pushed_at", "") >= "2025-01-01"
            ]
            
            # Sort by stars (desc) then pushed_at (desc)
            public_repos.sort(key=lambda x: (x.get("stargazers_count", 0), x.get("pushed_at", "")), reverse=True)
            
            return public_repos[:2]
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def generate_html(repos):
    html = '<div align="center">\n'
    for repo in repos:
        repo_name = repo["name"]
        html += f'  <a href="https://github.com/{USERNAME}/{repo_name}">\n'
        html += '    <picture>\n'
        html += f'      <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats-sigma-five.vercel.app/api/pin/?username={USERNAME}&repo={repo_name}&theme=radical&hide_border=true">\n'
        html += f'      <source media="(prefers-color-scheme: light)" srcset="https://github-readme-stats-sigma-five.vercel.app/api/pin/?username={USERNAME}&repo={repo_name}&theme=default&hide_border=true">\n'
        html += f'      <img src="https://github-readme-stats-sigma-five.vercel.app/api/pin/?username={USERNAME}&repo={repo_name}&theme=radical&hide_border=true" />\n'
        html += '    </picture>\n'
        html += '  </a>\n'
    html += '</div>'
    return html

def update_readme():
    repos = get_top_repos()
    if not repos:
        print("No repos found.")
        return

    new_content = generate_html(repos)
    
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            
        pattern = re.compile(f"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}", re.DOTALL)
        if not pattern.search(content):
            print("Markers not found in README.md")
            return

        updated_content = pattern.sub(f"{MARKER_START}\n{new_content}\n{MARKER_END}", content)
        
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
        print(f"Successfully updated Top Projects with: {[r['name'] for r in repos]}")
        
    except Exception as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    update_readme()
