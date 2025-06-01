# Mock Pricing Agent Web Application

A Flask web application that provides a secure web-based terminal interface to a command-line pricing agent application.

## Features

- **Web-based Terminal**: Access your console application through a modern web interface
- **Secure by Design**: Only exposes the specific console application, not the underlying shell
- **Session Management**: Each user gets their own isolated session
- **Container Ready**: Deployable as a Docker container
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python src/app.py
```

3. Open your browser to `http://localhost:5000`

4. Click "Open Console Terminal" to access the command-line interface

### Docker Deployment

1. Build the container:
```bash
docker build -t mockpricingagent-webapp .
```

2. Run the container:
```bash
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key mockpricingagent-webapp
```

3. Access the application at `http://localhost:5000`

## Console Application

The embedded console application (`console_app.py`) provides:

- **Price Calculator**: Calculate mock pricing for products
- **System Status**: View application status and version information
- **Interactive Interface**: Command-line interface with help system
- **Safe Termination**: Application terminates cleanly without shell access

### Available Commands

- `price` - Calculate mock pricing for a product
- `status` - Show system status and version
- `help` - Display help information
- `exit` - Exit the application

## Security Features

- **Process Isolation**: The console app runs in a separate subprocess
- **No Shell Access**: Users cannot access the underlying operating system shell
- **Automatic Cleanup**: Sessions are automatically terminated when users disconnect
- **Non-Root Container**: The Docker container runs as a non-privileged user
- **Session Management**: Each connection gets its own isolated environment

## Architecture

The application consists of:

1. **Flask Web Server** (`app.py`): Serves the web interface and manages WebSocket connections
2. **Terminal Interface** (`terminal.html`): Web-based terminal using xterm.js
3. **Console Application** (`console_app.py`): The actual command-line application
4. **Session Management**: Secure subprocess management with automatic cleanup

## Project Structure
```
mockpricingagent-webapp
├── src
│   ├── app.py               # Main entry point for the web application
│   ├── console_app.py       # Logic for the console application
│   ├── static               # Static files (CSS, JS)
│   │   ├── css
│   │   │   └── style.css    # Styles for the web application
│   │   └── js
│   │       └── main.js      # Client-side JavaScript
│   ├── templates            # HTML templates
│   │   └── index.html       # Main HTML template
│   └── config.py            # Configuration settings
├── Dockerfile                # Dockerfile for building the application image
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd mockpricingagent-webapp
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Copy `.env.example` to `.env` and fill in the required values.

5. **Run the Application**
   You can run the application using the following command:
   ```bash
   python src/app.py
   ```

## Docker Deployment
To deploy the application using Docker, follow these steps:

1. **Build the Docker Image**
   ```bash
   docker build -t mockpricingagent .
   ```

2. **Run the Docker Container**
   ```bash
   docker run -p 5000:5000 mockpricingagent
   ```

3. **Using Docker Compose**
   Alternatively, you can use Docker Compose to manage the application:
   ```bash
   docker-compose up
   ```

## Usage
Once the application is running, you can access it in your web browser at `http://localhost:5000`.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.