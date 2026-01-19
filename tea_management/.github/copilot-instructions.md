# Copilot Instructions for AI Coding Agents

## Project Overview
This project is a comprehensive management system for therapy evaluations, integrating various components such as user management, therapy recommendations, and diagnostic evaluations. The architecture is modular, with distinct apps for different functionalities:

- **apps/**: Contains the main application modules, each responsible for specific domains (e.g., `terapias`, `consultorios`, `usuarios`).
- **models.py**: Defines the data models used across the application, including relationships between different entities.
- **views.py**: Handles the business logic and data presentation for each module.

## Key Components
- **ValoracionInicial**: Central model for initial evaluations, linking to various assessments and diagnostics.
- **CodigoCIE10**: Represents the CIE-10 diagnostic codes, crucial for linking evaluations to standardized medical classifications.

## Developer Workflows
### Running Tests
To run tests, use the following command:
```bash
python -m pytest
```
This command will execute all tests defined in the `tests.py` files across the apps.

### Debugging
Utilize the built-in Django debugging tools. Set breakpoints in your views or models to inspect the flow of data and application state.

### Building the Application
Ensure all dependencies are installed by running:
```bash
pip install -r requirements.txt
```
This will set up the environment for development.

## Project Conventions
- **Naming Conventions**: Follow PEP 8 guidelines for naming variables and functions. Class names should use CamelCase, while variables and functions should use snake_case.
- **Documentation**: Each model and view should have docstrings explaining their purpose and usage.

## Integration Points
- **External Dependencies**: The project relies on Django for the web framework and various libraries for testing and data handling. Ensure these are included in your `requirements.txt`.
- **Cross-Component Communication**: Use Django signals for inter-component communication, especially for actions that require updates across different models (e.g., when a new therapy is added).

## Examples
- **Creating a New Evaluation**: To create a new evaluation, instantiate the `ValoracionInicial` model and link it to the appropriate `CodigoCIE10` instance.
- **Fetching Therapies**: Use the `terapias_recomendadas` field in `ValoracionInicial` to retrieve recommended therapies for a patient.

## Conclusion
These instructions should help AI coding agents understand the structure and workflows of this project, enabling them to assist effectively in development tasks.