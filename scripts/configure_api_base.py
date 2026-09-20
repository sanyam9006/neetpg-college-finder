def configure():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    # Add const API_BASE
    script_marker = '<script>\n'
    api_base_decl = '<script>\nconst API_BASE = (window.location.protocol === "file:") ? "http://localhost:8000" : "";\n'

    if "const API_BASE =" not in text:
        text = text.replace(script_marker, api_base_decl, 1)

    # Replace all occurrences of http://localhost:8000
    text = text.replace("fetch('http://localhost:8000/api/v1/auth/register'", "fetch(`${API_BASE}/api/v1/auth/register`")
    text = text.replace("fetch('http://localhost:8000/api/v1/auth/login'", "fetch(`${API_BASE}/api/v1/auth/login`")
    text = text.replace('fetch("http://localhost:8000/api/v1/feedback"', 'fetch(`${API_BASE}/api/v1/feedback`')
    text = text.replace('fetch("http://localhost:8000/api/v1/health"', 'fetch(`${API_BASE}/api/v1/health`')

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(text)

    print('API_BASE dynamic configuration applied successfully!')

if __name__ == '__main__':
    configure()
