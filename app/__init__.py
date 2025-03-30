from flask import Flask
import logging
import os

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Register blueprints - use the root URL prefix for simpler routing
    from app import routes
    app.register_blueprint(routes.bp, url_prefix='')
    
    # Log app initialization
    app.logger.info("Flask application initialized")
    
    return app 