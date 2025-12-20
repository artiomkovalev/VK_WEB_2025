def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    query_string = environ.get('QUERY_STRING', '')
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    response_body = f"GET parameters: {query_string}\nPOST data: {request_body.decode('utf-8')}\n"
    return [response_body.encode('utf-8')]
