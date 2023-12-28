# Family MTG Match Tracker - Proposal

The purpose of this proposal is to outline the plan for updating the existing Family Match Tracker application. The update involves addressing obsolete/modified libraries, refactoring the application into microservices, and implementing a containerized solution using Docker. Additionally, a daily update mechanism will be established to ensure the application stays up-to-date with the latest commits.

# Objectives

Refactor the monolithic application into three microservices:
- App Microservice: Contains the structure of the updated application.
- Database Microservice: Manages the storage and retrieval of data.
- Plot Microservice: Handles data retrieval, creates plot images, and displays them in the App Microservice.

Utilize Docker to package each microservice into separate containers for easy deployment and scalability.

Implement Docker-Compose to orchestrate the deployment and interaction of the three containers.

A CI/CD pipeline using GitHub Actions will be responsible for triggering the new deployment by accessing our virtual machine via SSH. From there, it will execute the 'docker-compose up' command, ensuring a cloud-native approach.


# Work distribution
- Alvaro: App microservice, cronjob
- Alejandra: Plot microservice, docker-compose
- Nestor: Database mircroservice, bash script

Certainly, every team member will actively contribute to the project's overall success, offering assistance to colleagues whenever necessary.

