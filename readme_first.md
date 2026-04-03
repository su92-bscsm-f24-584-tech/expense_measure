
# Expense Tracker App

A simple Python-based expense tracker app containerized with Docker. This ensures a consistent environment, so you don’t need to install Python or dependencies manually.

---

## Project Structure

money-tracker/
│
├─ app.py # Main application
├─ Expensemeasure.py # Expense management module
├─ requirements.txt # Python dependencies
├─ Dockerfile # Docker build instructions
└─ README.md # This file

yaml
Copy code


- [Docker](https://www.docker.com/get-started)
- Optional: [Git](https://git-scm.com/) to clone the repo

---

## Build Docker Image

From the project root:

```bash
docker build -t expense-app .
Run Docker Container
bash
docker run -it --name my-expense-app expense-app
-it: interactive terminal

--name my-expense-app: custom container name

Dependencies
All Python dependencies are listed in requirements.txt:

ini
Copy code
Flask==3.1.2
requests==2.31.0

matplotlib==3.8.0
Docker installs these automatically during build.