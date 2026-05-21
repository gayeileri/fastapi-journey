import language_tool_python

try:
    tool = language_tool_python.LanguageToolPublicAPI('en-US')
except Exception as e:
    tool = None
    print(f"WARNING: LanguageTool is currently unavailable (rate limit or connection issue). Grammar checking will be skipped.")

def check_grammar(text: str):
    if not tool:
        return []
    matches = tool.check(text)
    issues = []
    for match in matches:
        issues.append({
            "issue": match.message,
            "context": match.context,
            "suggestions": match.replacements[:5],
            "offset": match.offset,
            "length": match.errorLength
        })
    return issues
