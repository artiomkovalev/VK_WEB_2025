def application(_, start_response):
    file_path = 'static/example.txt'
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        status = '200 OK'
        headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(content)))
        ]
    except FileNotFoundError:
        status = '404 Not Found'
        content = b'File not found'
        headers = [('Content-type', 'text/plain')]

    start_response(status, headers)
    return [content]
