import requests
from bs4 import BeautifulSoup

def fetch_updates():
    url = "https://ffxileveldown.fandom.com/wiki/Update"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        updates = []
        
        # Modify this to target the specific HTML elements that contain update info
        update_sections = soup.find_all("div", {"class": "mw-parser-output"})
        for section in update_sections:
            headers = section.find_all(["h2", "h3"])  # Find headers (modify if needed)
            paragraphs = section.find_all("p")
            
            for header, paragraph in zip(headers, paragraphs):
                title = header.get_text(strip=True)
                description = paragraph.get_text(strip=True)
                updates.append({"title": title, "description": description})
        
        return updates
    else:
        print("Failed to fetch updates.")
        return []

