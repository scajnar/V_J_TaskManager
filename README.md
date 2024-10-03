[#](#) QA Engineer Assignment: Login Test with Playwright, Python, and Docker

## Objective
Create an automated test using Playwright and Python to verify the functionality of a "Task Manager" web app. The tests should be performed inside a Docker container (Dockerfile included) and automatically start when the container is run.

The app is included in the repo (see tasks.html) or on the URL https://demo.visionect.com/tasks/index.html

## Requirements

### 1. Test Cases
Implement a test case that does the following:

- After the page is loaded, the "Daily Tip" should load within one second (it shows the text "Stay focused and prioritize your most important tasks!")
- If user adds a new task by entering a task name and clicking on the "Add Task" button, the created task should appear in the "Task List" section
- If a user finishes a task (clicks on the checkbox besides the task) and then clicks on the "Show Completed Tasks" button, the finished task name should appear blow the "Show Completed Tasks" button within 10 seconds.

### 2. Technology Stack
- Playwright
- Python
- Docker

### 3. Implementation Details
- Add screenshots or video recording of failed tests
- Implement a simple HTML report generator for test results
- Use Playwright's Python API to interact with the web page
- Implement appropriate wait strategies to ensure elements are loaded before interacting with them
- Use assertions to verify the presence of the error message
- Implement proper error handling and logging
- Follow PEP 8 style guidelines for Python code

### 4. Docker Integration
- Use the provided Dockerfile and set up the environment necessary to run the test
- Provide clear instructions on how to build and run the Docker container

### 5. Documentation
- Include a INSTRUCTIONS.md file with:
    - A brief explanation of the test cases
    - Instructions for setting up and running the test using Docker
    - Any assumptions or limitations of the current implementation
    - Suggestions for potential improvements or extensions to the test suite

## Deliverables
- Python script(s) containing the Playwright test
- INSTRUCTIONS.md with documentation
- Any additional configuration files or dependencies

## Evaluation Criteria
- Correctness of the test implementation
- Code quality and adherence to best practices
- Effective use of Playwright features
- Proper integration with Docker
- Quality and clarity of documentation
- Handling of edge cases and error scenarios