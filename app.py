from application import create_app
import os

# Get the configuration name from environment variable or use 'default'
config_name = os.getenv('FLASK_CONFIG', 'default')

# Create the Flask app instance using the Application Factory Pattern
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
