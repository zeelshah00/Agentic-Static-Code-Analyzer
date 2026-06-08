<!-- Future Functionality:

Analyzer Logic Improvement (potentially use Regex or using API for data)
Automatic Language Detection
CSV global variable
Additional Language Support
Give GPT written language instead of raw data
Prevent Blank Submission -->




# Code Protect - AI
#### Description: 

CodeProtect AI is a web application designed to help developers identify potential security vulnerabilities in their code before deploying it. The goal of this project is to provide a simple, educational tool that demonstrates how common security issues can be detected automatically and explained in a way that developers can easily understand. The application allows users to paste a snippet of code into a web interface, select the programming language, and receive a report highlighting possible security risks along with explanations and remediation suggestions.

Modern software development often moves quickly, and security issues can easily be overlooked, especially by beginner developers. Tools known as Static Application Security Testing (SAST) tools are commonly used in professional environments to analyze code and detect vulnerabilities before deployment. CodeProtect AI is inspired by these tools but intentionally simplified to make it easier to understand how such systems work internally. The application combines rule-based vulnerability detection with AI-generated explanations and remediation steps to produce helpful and readable results.

The project was built using concepts and technologies learned throughout CS50, including Python, Flask, HTML, CSS, SQL, and APIs. It demonstrates full-stack web development while also incorporating modern AI capabilities.

---

## Features

The main functionality of CodeProtect AI includes:

* **Code submission interface** where users can paste code snippets for analysis
* **Language selection** to support multiple programming languages such as Python and JavaScript
* **Rule-based vulnerability detection** that scans code for insecure patterns
* **AI Powered recommendations** that suggest safer coding practices
* **Scan history storage** using SQLite so users can review past analyses

The analyzer currently focuses on detecting several common security vulnerabilities including:

* SQL Injection
* Dangerous use of `eval()` or `exec()`
* Use of `subprocess(..., shell=True)`
* Hardcoded credentials or API keys
* Unsafe DOM manipulation in JavaScript such as `innerHTML`

These checks are implemented using pattern matching and simple parsing logic to identify risky code structures.

---

## Project Architecture

The application follows a simple web architecture. The frontend provides a form where users submit their code, while the backend processes the submission and performs the analysis. The backend then returns the findings and explanations to be displayed on a results page.

The overall flow works as follows:

1. A user submits a code snippet through the web interface.
2. Flask receives the code and language selection.
3. The backend runs rule-based security checks to detect known vulnerability patterns.
4. The detected findings are passed to an AI model that generate remediation suggestions.
5. The results are displayed to the user and stored in the SQLite database.

This architecture ensures that the application remains functional even if the AI service is unavailable because the primary detection logic is rule-based.

---

## File Structure and Responsibilities

The project is organized into several files and directories to separate concerns and maintain clean code structure.

### `app.py`

This file contains the main Flask application and defines all routes for the web server. It handles HTTP requests, receives user-submitted code, calls the analysis functions, and renders the HTML templates for displaying results. It also manages database interactions for storing scan history.

### `analyzer.py`

The `analyzer.py` file contains the core analysis logic for the application. This includes functions that scan the submitted code for suspicious patterns and return a structured list of findings. Each finding includes a title, severity level, line number, and explanation.

Separating this logic into a helper module keeps the Flask routes clean and makes the analysis functions easier to maintain and expand.

### `prompts.py`

This file stores the AI prompt templates used when generating remediation suggestions. By isolating prompts in a separate file, the project keeps AI-related logic organized and makes it easier to modify prompts without changing the main application logic.

### `templates/`

The templates directory contains HTML files used by Flask to render pages.

* **index.html** – The homepage where users paste their code and choose a language for analysis.
* **results.html** – Displays the vulnerability findings and explanations after analysis.
* **history.html** – Shows previously analyzed code snippets stored in the database.
* **base.html** – A base template used to maintain consistent structure across pages.

### `static/`

This folder contains static assets such as CSS files used to style the web interface. The styling improves readability and visually highlights different severity levels for detected vulnerabilities.


### `requirements.txt`

This file lists all Python dependencies required to run the project. It allows others to easily install the correct packages using `pip install -r requirements.txt`.

---

## Design Decisions

Several design decisions were made during development.

One key decision was to use rule-based detection as the primary vulnerability detection method instead of relying entirely on AI. While AI models are powerful, they can sometimes produce inconsistent or incorrect results. By implementing rule-based detection first, the system ensures consistent and predictable vulnerability detection. AI is then used only to explain the findings and suggest improvements.

Another important design choice was to keep the project focused on a small number of common vulnerabilities instead of trying to support every possible security issue. This keeps the code manageable while still demonstrating how automated security analysis works.

The project also stores scan results in a SQLite database, which allows users to review previous analyses and demonstrates the use of relational databases within a Flask application.

Finally, the application was designed with modularity in mind. By separating the Flask routes, analysis logic, AI prompts, templates, and database interactions into different files and directories, the project becomes easier to understand and maintain.

---

## Future Improvements

There are several possible improvements that could extend this project further.

Future versions could include support for additional programming languages, more advanced vulnerability detection techniques, integration with public vulnerability databases, or automated code fixes generated by AI. The system could also be expanded into a browser extension or integrated directly into development environments.

---

## Conclusion

CodeProtect AI demonstrates how automated security tools can help developers write safer code. By combining rule-based vulnerability detection with AI-generated explanations, the project provides an educational and practical tool for understanding common security risks in software development.

This project reflects concepts learned throughout CS50, including web development, database management, APIs, and software design. It also introduces modern AI integration, illustrating how traditional programming techniques and machine learning tools can work together to create useful developer tools.
