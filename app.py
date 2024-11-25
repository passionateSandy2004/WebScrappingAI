from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def scrape_portfolio(url):
    """
    Scrapes a portfolio webpage and extracts meaningful content.
    
    Parameters:
        url (str): The URL of the portfolio webpage.
    
    Returns:
        dict: A dictionary containing the summary of extracted data.
    """
    # Fetch the webpage
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
    # Parse the webpage content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract meaningful data
    title = soup.title.string.strip() if soup.title else "No title found"
    headings = [h.get_text(strip=True) for h in soup.find_all(re.compile(r'h[1-6]'))]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    links = [{'text': a.get_text(strip=True), 'href': a['href']} 
             for a in soup.find_all('a', href=True)]
    images = [img['src'] for img in soup.find_all('img', src=True)]
    
    # Summarize the extracted data
    summary = {
        "title": title,
        "headings": headings[:10],  # First 10 headings
        "content_snippet": ' '.join(paragraphs[:3]),  # First 3 paragraphs as a snippet
        "num_links": len(links),
        "links": links[:5],  # Show first 5 links
        "num_images": len(images),
        "image_urls": images[:5],  # Show first 5 image URLs
    }
    
    return summary

@app.route('/scrape', methods=['POST'])
def scrape():
    """
    API endpoint to scrape a portfolio webpage.
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Please provide a valid URL in the request body."}), 400
    
    url = data['url']
    try:
        summary = scrape_portfolio(url)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
