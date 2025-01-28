# Deployment Plan for Property Valuation Application

This document outlines the deployment strategy for the 2022 Durban property valuation
application, detailing how to schedule scrapers, deploy the API to production, and handle errors,
downtime, and alerts.

## 1. Scheduling the Scrapers

To ensure daily data extraction and seamless operation, the scrapers will be scheduled using
the following approach:

- **Job Scheduling** : The application will use the **APScheduler** library to schedule tasks.
    The scrapers will be configured to run daily by setting the EXTRACTION_INTERVAL in
    the .env file to 1.
- **Alternatively,** for improved scalability and reliability:
    - **Celery** : Configure the scraper as a task, using **Redis** or **RabbitMQ** as the
       message broker. The task will run daily as part of a worker process.
    - **Kubernetes CronJob** : On a Kubernetes cluster, define a CronJob to execute the
       scraper at a specified time. This setup ensures resiliency in case of container
       failures.

## 2. Deploying the API to Production

The API, developed using **FastAPI** , will be deployed as a production-ready service leveraging
modern cloud infrastructure.

### Deployment Framework

- **Server Setup** : The API will use **Gunicorn** with **Uvicorn workers** to handle high
    concurrency and optimize performance in a production environment.

### Cloud Provider

- **AWS (Amazon Web Services)** as the cloud provider for deployment. The infrastructure
    includes:
       - **Amazon ECS (Elastic Container Service)** : Used to deploy the containerized
          application. **Fargate** will be utilized for a serverless approach, removing the need
          for instance management.
       - **Amazon RDS (Relational Database Service)** : A managed PostgreSQL
          database to store property data with built-in scalability, backups, and monitoring.


### Deployment Steps

1. **Containerization** :
    - The application will be packaged using Docker. The existing Dockerfile will be
       optimized for production use.
2. **CI/CD Pipeline** :
    - A continuous integration and deployment (CI/CD) pipeline will be set up using
       **GitHub Actions** or **AWS CodePipeline**.
    - The pipeline will automate building and pushing the Docker image to **Amazon**
       **ECR (Elastic Container Registry)**.
3. **Service Deployment** :
    - Deploy the Docker container using Amazon ECS with health checks, load
       balancing, and autoscaling policies.
    - Integrate an **Application Load Balancer (ALB)** to expose the API securely via
       HTTPS.

### Architecture

The deployment architecture will consist of the following:

- **API Layer** : The FastAPI application deployed on ECS with autoscaling.
- **Database Layer** : Amazon RDS for PostgreSQL, configured for high availability and
    durability.
- **Networking** : An Application Load Balancer to handle incoming requests and provide
    SSL termination for secure connections.

## 3. Handling Errors, Downtime, and Alerts

### Error Handling

- The application logs will be integrated with **Amazon CloudWatch Logs** for centralized
    monitoring and analysis.
- Errors during scraper execution will trigger email alerts using the SMTP configuration
    already defined in the .env file.

### Downtime Mitigation

- **Rolling Deployments** : ECS will be configured for rolling updates to ensure zero
    downtime during API updates or changes.
- **Autoscaling Policies** : Both the API and database layers will leverage AWS autoscaling
    to handle fluctuations in traffic and load.

### Alerts and Monitoring

- **Amazon CloudWatch Alarms** will be configured to monitor:


- API health metrics (latency, error rates).
- Database performance (CPU usage, connection limits).
- Alerts will be sent using **Amazon SNS (Simple Notification Service)** to notify
administrators via email or SMS.
- For scraper-specific issues, error notifications will be sent to the configured recipient
email in .env.