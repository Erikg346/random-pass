# Policy Service

This directory contains the implementation of the Policy Service, which is responsible for managing password policies in the random password microservices architecture.

## Overview

The Policy Service provides an API for creating, updating, and retrieving password policies. It ensures that generated passwords adhere to specified rules and guidelines.

## Features

- Create new password policies
- Update existing password policies
- Retrieve password policies
- Integration with observability tools for monitoring

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd random-pass-microservices/policy-service
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service**:
   ```bash
   python src/app.py
   ```

4. **Access the API**:
   The service will be available at `http://localhost:5000` (or the configured host and port).

## Usage Examples

- **Create a new policy**:
  ```http
  POST /policies
  Content-Type: application/json

  {
      "name": "Strong Policy",
      "min_length": 12,
      "require_uppercase": true,
      "require_special": true
  }
  ```

- **Retrieve all policies**:
  ```http
  GET /policies
  ```

## Observability

This service is integrated with OpenTelemetry for tracing and metrics. Ensure that the observability tools are set up correctly to monitor the service's performance and health.

## License

This project is licensed under the MIT License. See the LICENSE file for details.