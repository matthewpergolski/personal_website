"""
Application entry point for both development and production
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    import os
    
    # Use environment variables with defaults for development
    port = int(os.environ.get('PORT', 5002))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(port=port, host=host, debug=debug) 