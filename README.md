# Asar Chatbot Design Platform

<img src="img/asar_logo.png" style="width: 30%;">

## Introduction

Asar is a lightweight chatbot design platform that integrates with Raspberry Pi to provide an end-to-end deployment workflow for chatbot services. With just a single-board computer, developers can easily create their own custom chatbot.

Traditionally, building chatbot services required knowledge in multiple programming languages and technical domains. Asar significantly lowers this barrier.

Asar’s system architecture adopts a containerized design for rapid development and deployment. For natural language processing, Asar leverages modern deep learning technologies such as Transformer and ALBERT to enable natural language understanding. For the developer experience, Asar offers a dedicated visual design tool that allows developers to create chatbot scripts using flowcharts and drag-and-drop programming blocks to control Raspberry Pi peripherals. Furthermore, Asar provides integrations with major messaging platforms, simplifying the process of embedding the chatbot into chatrooms.Asar runs entirely on the Raspberry Pi, requiring no external services, thereby reducing the risk of personal data leakage. Thanks to the Raspberry Pi's flexibility and expandability, Asar can be applied to a variety of scenarios.

For more detailed information, please refer to the [video](https://youtu.be/qPC17DJIEco?si=SCVBBVSocsZHTrEl), report ([Simplified](doc/實務專題報告書(精簡版).pdf), [Full version](doc/實務專題報告書.pdf)), and the [User Manual](doc/操作手冊.pdf).

## Deployment Guide

1. Prepare your Raspberry Pi
    - Supported Models: 4B, 400
    - RAM Requirement: 4GB or more
    - OS: Raspberry Pi OS (64-bit)

2. Install Docker and Docker-Compose
    - [Docker Install documentation](https://docs.docker.com/install/)
    - [Docker-Compose Install documentation](https://docs.docker.com/compose/install/)

3. Create `docker-compose.yml`

    ```yml
    version: "3.8"

    networks:
      default:
        name: asar-prod

    volumes:
      rasa:    # Stores chatbot service data
      actions: # Stores action server data
      data:    # Stores backend API service data

    services:
      rasa: # Chatbot Service
        image: devilhyt/rasa:custom
        volumes:
          - rasa:/app
          - data:/data
        ports:
          - 5005:5005

      action: # Action Server
        image: devilhyt/rasa-sdk:custom
        volumes:
          - actions:/app/actions
        ports:
          - 5055:5055
        privileged: true

      api: # Backend API Service
        image: devilhyt/asar-api:latest
        volumes:
          - actions:/actions
          - data:/data
        environment:
          SECRET_KEY: # Flask secret key
          # Generate with: python -c 'import secrets; print(secrets.token_hex())'
          ASAR_USERNAME: admin # Admin username
          ASAR_PASSWORD: admin # Admin password
          RASA_API_HOST: rasa  # Hostname of the chatbot service
          ASAR_API_HOST: api   # Hostname of the backend API service
        ports:
          - 5500:5500

      web: # Frontend Web Service
        image: devilhyt/asar-web:latest
        environment:
          RASA_API_HOST: rasa # Hostname of the chatbot service
          ASAR_API_HOST: api  # Hostname of the backend API service
        ports:
          - 80:80
        depends_on:
          - api
    ```

4. Start the services

    ```bash
    docker-compose up -d

    # If using docker-compose-plugin
    docker compose up -d
    ```

5. Log in to the Asar platform

    - http://127.0.0.1
    - http://localhost
    - http://raspberrypi

6. Start designing your chatbot

## Docker Environment Variables

### Backend API Service

- Required Settings
    - `SECRET_KEY`:               API secret key for securing session cookies
    - `ASAR_USERNAME`:            Admin username
    - `ASAR_PASSWORD`:            Admin password
    - `RASA_API_HOST`:            Hostname of the chatbot service
    - `ASAR_API_HOST`:            Hostname of the backend API service

- Advanced Settings  
    - `RASA_API_PROTOCOL`:        Protocol for chatbot service (http/https)
    - `RASA_API_PORT`:            Port for chatbot service
    - `ASAR_API_PROTOCOL`:        Protocol for API service (http/https)
    - `ASAR_API_PORT`:            Port for API service
    - `RASA_API_AGENT_PROTOCOL`:  Protocol for chatbot proxy
    - `RASA_API_AGENT_HOST`:      IP address of chatbot proxy
    - `RASA_API_AGENT_PORT`:      Port of chatbot proxy
    - `ASAR_API_AGENT_PROTOCOL`:  Protocol for API service proxy
    - `ASAR_API_AGENT_HOST`:      Hostname for API service proxy
    - `ASAR_API_AGENT_PORT`:      Port of API service proxy
    - `RASA_ACTIONS_ROOT`:        Root directory for action server

### Frontend Web Service

- Required
    - `RASA_API_HOST`:            Hostname of the chatbot service
    - `ASAR_API_HOST`:            Hostname of the backend API service

- Advanced Settings
    - `RASA_API_PROTOCOL`:        Protocol for chatbot service (http/https)
    - `RASA_API_PORT`:            Port for chatbot service
    - `ASAR_API_PROTOCOL`:        Protocol for backend API service (http/https)
    - `ASAR_API_PORT`:            Port for backend API service

## Project Structure

```
    .
    ├── rasa                            # Chatbot service
    │   ├── build                       # Dependency files
    │   │   └── initial_project_zh      # Rasa configuration files and custom tools
    │   │       ├── custom_components   # NLP components
    │   │       ├── custom_connectors   # Chat platform interfaces
    │   │       └── ...
    │   └── Dockerfile
    ├── rasa-sdk                        # Action server
    │   ├── app                         # Initial project
    │   │   └── actions
    │   ├── rasa-sdk                    # Main program of action server (submodule)
    │   ├── requirements.txt            # Python dependencies
    │   └── Dockerfile
    ├── api                             # Backend API service
    │   ├── app                         # Main program of API (submodule)
    │   └── Dockerfile
    ├── web                             # Frontend web service
    │   ├── app                         # Main program of web (submodule)
    │   ├── templates                   # Nginx configuration templates
    │   └── Dockerfile
    ├── docker-compose-dev.yml          # Compose file for development environment
    ├── docker-compose-prod.yml         # Compose file for production environment
    ├── doc                             # Documentation
    ├── demo                            # Example project
    └── ...
```

# Contributors

- HsiangYi Tsai, [devilhyt](https://github.com/devilhyt) on GitHub  
- Paxton, [Paxton90](https://github.com/Paxton90) on GitHub