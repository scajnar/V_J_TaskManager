# Automated Testing for the Task Manager Web Application

This repository contains automated tests for the "Task Manager" web application using Playwright and Python. The tests verify key functionalities of the app and are designed to run inside a Docker container for consistency and ease of setup.

## Table of Contents

- [Overview](#overview)
- [Test Cases](#test-cases)
- [Setup and Running Tests](#setup-and-running-tests)
- [Assumptions and Limitations](#assumptions-and-limitations)
- [Potential Improvements](#potential-improvements)
- [Code Structure](#code-structure)

## Overview

The automated tests are designed to verify the core functionalities of the "Task Manager" web application, ensuring that:

- The **"Daily Tip"** loads within a specified time.
- New tasks can be added and appear in the **"Task List"**.
- Tasks can be marked as completed and appear under **"Completed Tasks"**.
- An alert is displayed when setting a task's priority.

The tests are implemented using Playwright for browser automation and pytest for structuring the tests.

## Test Cases

### 1. Verify Daily Tip Loading

- **Objective:** Ensure that the "Daily Tip" loads within specified timeouts.
- **Description:**
  - After navigating to the Task Manager page, the test waits for the "Daily Tip" text to appear.
  - Verifies that the text matches **"Stay focused and prioritize your most important tasks!"** within various timeouts (1s, 2s, 3s, 4s).

### 2. Add New Task

- **Objective:** Verify that adding a new task displays it in the **"Task List"** section.
- **Description:**
  - Inputs various task names into the **"Add New Task"** field and clicks the **"Add Task"** button.
  - Checks if the task appears in the **"Task List"** with the correct text.

### 3. Mark Task as Completed

- **Objective:** Ensure that a completed task appears under **"Completed Tasks"** when requested.
- **Description:**
  - Adds a new task and marks it as completed.
  - Clicks on the **"Show Completed Tasks"** button.
  - Verifies that the completed task appears in the list within various wait times.

### 4. Check Alert Presence

- **Objective:** Verify that an alert is displayed when setting a task's priority.
- **Description:**
  - Adds a new task and clicks the **"Set Priority"** button.
  - Handles the alert dialog and asserts that the correct alert message is displayed.

## Setup and Running Tests

### Prerequisites

- **Docker:** Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/get-started).

### Steps

1. **Clone the Repository**

 ```
 git clone https://github.com/yourusername/task-manager-tests.git
 cd task-manager-tests
 ```

1. **Build the Docker Image**


```
Copy code
docker build -t task-manager-tests .
Run the Docker Container
```


1. **Run the Docker container to execute the tests**

````
Copy code
docker run --rm -it -v "$(pwd)/reports:/app" task-manager-tests
````
  
Explanation:

--rm: Automatically removes the container after it exits.  
-it: Runs the container in interactive mode.  
-v "$(pwd)/reports:/app": Maps the reports directory in your current path to the /app directory in the container, allowing you to access the test reports.
### View the Test Report

After the tests have completed, an HTML report named report.html will be generated in the reports directory.

Open reports/report.html in a web browser to view the test results.

### Assumptions and Limitations
- Single Browser Testing: The tests are configured to run using the Chromium browser only.  
- Limited Error Handling: The current implementation may not handle all edge cases or network failures gracefully.  
### Potential Improvements
- Multi-Browser Support: Extend the tests to run on additional browsers like Firefox and WebKit to ensure cross-browser compatibility.
- Enhanced Error Handling: Implement more robust error handling to manage network timeouts, element not found exceptions, and other runtime errors.
CI/CD Integration: Integrate the test suite with a continuous integration system like Jenkins or GitHub Actions for automated testing on code changes.
Parameterized Configurations: Externalize configurations (like URLs, timeouts) to a configuration file for easier maintenance.
Reporting Enhancements: Incorporate more detailed reporting tools or integrate with dashboards for better visualization over time.
### Code Structure
**test_task_manager.py**: The main test script containing all test cases.  
**Dockerfile**: Contains instructions to set up the Docker image with all dependencies.  
**reports/**: Directory where test reports are stored after execution.
