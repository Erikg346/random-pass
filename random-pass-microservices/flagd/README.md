# Flagd Feature Flag Service

This directory contains the implementation and configuration for the feature flag service used in the random-pass-microservices architecture.

## Overview

The feature flag service allows for dynamic feature management across the microservices. It enables developers to toggle features on or off without deploying new code, facilitating A/B testing and gradual rollouts.

## Setup Instructions

1. **Configuration**: 
   - Modify the `config/flags.json` file to define your feature flags. Each flag should have a unique key and a boolean value indicating whether the feature is enabled or disabled.

2. **Running the Service**:
   - Ensure you have the necessary dependencies installed.
   - Start the service using your preferred method (e.g., Docker, directly with Python).

3. **Integration**:
   - Each microservice can query the feature flag service to check the status of specific flags and adjust behavior accordingly.

## Usage Examples

- To check if a feature is enabled, make a request to the feature flag service endpoint with the feature key.
- Use the feature flags to control access to new features for specific user segments or environments.

## Additional Resources

- [Feature Flagging Best Practices](https://featureflags.dev)
- [OpenTelemetry Integration](https://opentelemetry.io/docs/instrumentation/) for observability in feature flag usage.