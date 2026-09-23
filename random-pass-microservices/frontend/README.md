# Frontend Microservices Documentation

This directory contains the frontend application for the Random Password Microservices project. The frontend is built using React and TypeScript, providing a user interface for interacting with the password generation API and other services.

## Project Structure

- `src/`: Contains the source code for the frontend application.
  - `App.tsx`: The main entry point of the application, responsible for setting up routing and rendering components.
  - `components/`: Contains reusable React components.
    - `PasswordGenerator.tsx`: A component for generating passwords by interacting with the password API.
  - `types/`: Contains TypeScript interfaces and types used throughout the application.
    - `index.ts`: Exports the types used in the application.

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd random-pass-microservices/frontend
   ```

2. **Install dependencies**:
   ```
   npm install
   ```

3. **Run the application**:
   ```
   npm start
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:3000` to view the application.

## Usage

The frontend application allows users to generate passwords by specifying the desired length. It communicates with the password API to fetch generated passwords and display them to the user.

## Development

For development purposes, you can modify the components in the `src/components` directory and the main application logic in `App.tsx`. Ensure to follow best practices for React and TypeScript.

## Testing

To run tests, use the following command:
```
npm test
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.