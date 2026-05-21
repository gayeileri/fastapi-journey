import markdown

def convert_to_html(markdown_content: str) -> str:
    return markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])

