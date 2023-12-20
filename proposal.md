# Family MTG Match Tracker - Proposal

The purpose of this proposal is to outline the plan for updating the existing Family Match Tracker application. The update involves addressing obsolete/modified libraries, refactoring the application into microservices, and implementing a containerized solution using Docker. Additionally, a daily update mechanism will be established to ensure the application stays up-to-date with the latest commits.

# Objectives
Identify and update obsolete/modified libraries in the existing codebase.

Refactor the monolithic application into three microservices:
- App Microservice: Contains the structure of the updated application.
- Database Microservice: Manages the storage and retrieval of data.
- Plot Microservice: Handles data retrieval, creates plot images, and displays them in the App Microservice.

Utilize Docker to package each microservice into separate containers for easy deployment and scalability.

Implement Docker-Compose to orchestrate the deployment and interaction of the three containers.

Bash script that checks for a new version of the deployed container.
If a new version is found, deletes the current container and downloads the latest version.

Set up a daily cronjob in a Windows Subsystem for Linux (WSL) environment to execute the update script.
