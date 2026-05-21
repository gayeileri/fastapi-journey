from bs4 import BeautifulSoup
from app.services.markdown_service import convert_to_html

def extract_plain_text(markdown_content: str) -> str:
    html = convert_to_html(markdown_content)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=' ')
