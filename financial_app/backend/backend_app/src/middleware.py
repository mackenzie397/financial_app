from flask import request

def set_csp_header(response):
    # Check if the request path is for Swagger UI
    if request.path.startswith('/apidocs') or request.path.startswith('/flasgger_static'):
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Allow inline scripts for Swagger
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "  # Allow Google Fonts
            "img-src 'self' data:; "
            "font-src 'self' https://fonts.gstatic.com; "  # Allow Google Fonts
            "connect-src 'self';"
        )
    else:
        # Strict CSP for the main application
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; " # Removed 'unsafe-inline' for the main app for better security
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self';"
        )
    response.headers['Content-Security-Policy'] = csp
    return response
