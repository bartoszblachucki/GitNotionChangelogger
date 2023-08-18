import requests

DATABASE_ID = "292dd4e8e0b3432d9c5014294a5f7a7d"

def get_pages(token):

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if 'object' in data and data['object'] == 'error':
        raise Exception(data['message'])

    # Comment this out to dump all data to a file
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results

def get_issues(token):
    pages = get_pages(token)
    issues = []

    for page in pages:
        props = page["properties"]
        issue_id = page["properties"]["ID"]["unique_id"]
        issue_id_str = f"{issue_id['prefix']}-{issue_id['number']}"
        issue_url = page["url"]
        issues.append((issue_id_str, issue_url))

    return issues
    
