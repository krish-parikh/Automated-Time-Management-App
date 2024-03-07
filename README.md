# Automated Time Management App Backend

## Introduction

This repository contains the backend functionality for an automated time management application. It leverages GPT-3.5 for event extraction and prioritisation, facilitating efficient calendar management and event scheduling.

## Components

### `model.py`

This module contains the model for event extraction, utilizing GPT-3.5. By modifying the schema in `model.py`, you can customize the system to extract specific types of events based on your requirements.

### `input.py`

Contains preprocessing functions that convert the GPT response into a consistent format for API responses. This module can be adapted to handle specific user inputs, such as specifying days in the future ("Thursday in 2 weeks").

### `priority.py`

Implements the prioritization algorithm that resolves conflicting events. It assesses the movability of events, prioritizing immovable events over movable ones. When events have the same movability, it compares priority levels and timestamps to determine which event should be rescheduled.

### Pipeline Function

This is the core function that integrates the modules mentioned above. It processes natural language prompts and applies the necessary changes to the database accordingly.

## Database Schema

The application uses a SQLite database, `calendar_db`, to manage user accounts and store events. Below is the schema used for the database:

# Database Schema

## `events` Table

| Field              | Type      | Constraints           |
|--------------------|-----------|-----------------------|
| `id`               | INTEGER   | PRIMARY KEY AUTOINCREMENT |
| `user_id`          | INTEGER   |                       |
| `event_name`       | TEXT      |                       |
| `start_datetime`   | DATETIME  |                       |
| `end_datetime`     | DATETIME  |                       |
| `event_date`       | DATE      | NOT NULL              |
| `event_flexibility`| INTEGER   | NOT NULL              |
| `event_importance` | INTEGER   | NOT NULL              |

## `users` Table

| Field       | Type    | Constraints               |
|-------------|---------|---------------------------|
| `id`        | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `username`  | TEXT    | NOT NULL UNIQUE           |
| `password`  | TEXT    | NOT NULL                  |
| `email`     | TEXT    |                           |

## Usage

### `main.py`

Serves as the entry point for the user management API. It handles the creation, updating, and deletion of events.

### `test_request.py`

Use this script to test the APIs in Python. Alternatively, you can use the FastAPI documentation for testing endpoints.

## Installation

To set up the backend on your local machine:

1. Clone the repository: 
2. Install the required dependencies: requirements.txt
3. Change .env file with your API Keys
4. Run main.py using command uvicorn main:app --reload
5. Navigate to http://127.0.0.1:8000/docs in your browser to interact and test the functions (alternativly you can use test_request.py file to test directly in python)
