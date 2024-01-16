# Family MTG Match Tracker

Family Match Tracker is a monolithic web application developed 3 years ago using Flask, SQLAlchemy, and Plotly. The primary purpose of this application is to provide a platform for tracking and analyzing results of matches played among family members. The app allows users to create accounts, manage decks, record match outcomes, and view detailed statistics for each deck and against each opponent.

# Team Members
- *Alvaro Juan Gomez*
- *Alejandra Gillet*
- *Nestor Miguel*
  
# Proposal

Please refer to the [proposal.md](https://github.com/Aljuagme/WS23_CloudComputing/blob/main/proposal.md) file for a detailed overview of the project, including its objectives, scope, and key features.

# Documentation

This project is a Flask-based web application designed to track results for MTG card games. It follows a microservices architecture, consisting of three containers:

- Container A: Contains the main application for tracking results.
- Container B: Displays statistics based on users performance.
- Container C: Utilizes PostgreSQL for storing user data, results, decks, etc.

## Endpoints

- /login: Start of the application, login with your credentials or register a new user.
- /register: Register a new user by specifying a username, password, and confirm password.
- /magic: Shows the last results of the matches played, along with who is the best player and best deck.
- /stats/id: Shows personal statistics about the logged-in user regarding general performance against other players and per deck.
- /decks: Shows the best 3 decks of all players and their stats.
- /magic_result: Add the result of a match.
- /add_deck: Add a deck to a user.
- /chart: Plots the win ratio per player in the last 30 days.

# Getting Started
## Prerequisites

- Docker installed on your machine.
- Docker Compose installed on your machine.
- GitHub Actions set up for the repository.
- Account in Amazon EC2 - AWS

## Installation
### Clone the repository
> ``` git clone git@github.com:Aljuagme/WS23_CloudComputing.git ```

> ``` cd WS23_CloudComputing/workflows ```

### Build and run the Docker containers
``` docker-compose up -d ```

This command will start all three containers in detached mode.

# GitHub Action Pipeline
The project utilizes GitHub Actions for automated deployment. The pipeline is triggered on commits to the main branch and includes the following stages:

- Build Docker Images: Builds Docker images for each microservice.
- Push Images to Docker Hub: Pushes the built images to Docker Hub.
- Deploy to Server: Connects to the deployment server, in our case EC2 from Amazon and runs *docker-compose up* to have up-and-running the latest version of the application.