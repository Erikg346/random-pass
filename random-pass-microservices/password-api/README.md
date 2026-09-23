# Password API

This is the Password API microservice, which is responsible for generating secure passwords. It provides endpoints to generate passwords, check the health of the service, and retrieve the API version.

## Features

- Generate random passwords with customizable lengths.
- Cache generated passwords using Redis for improved performance.
- Health check endpoint to monitor service status.
- Version endpoint to retrieve the current API version.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd random-pass-microservices/password-api
   ```

2. **Install dependencies:**
   Ensure you have Python 3.7+ and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Redis:**
   Make sure you have a Redis server running. You can use Docker to run Redis:
   ```bash
   docker run -d -p 6379:6379 redis
   ```

4. **Run the application:**
   Start the Flask application:
   ```bash
   python app.py
   ```

5. **Access the API:**
   The API will be available at `http://localhost:5000`. You can use tools like Postman or curl to interact with the endpoints.

## Usage Examples

- **Generate a password:**
  ```bash
  curl "http://localhost:5000/generate-password?length=16"
  ```

- **Check health:**
  ```bash
  curl "http://localhost:5000/health"
  ```

- **Get API version:**
  ```bash
  curl "http://localhost:5000/version"
  ```

## Observability

This service is instrumented with OpenTelemetry for tracing and metrics. Ensure that the OpenTelemetry collector is set up to collect and export telemetry data.

## License

This project is licensed under the MIT License. See the LICENSE file for details.