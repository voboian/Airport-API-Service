# Airport-API-Service

## Project Description
The Airport API Service is a Django REST-based project designed to provide comprehensive flight management and tracking capabilities. 
It offers a robust API for accessing and managing data related to airports, airplanes, flights, routes, and orders.

## Installation and Setup

### Dependencies
- Python 3.x
- Django 3.x or higher
- djangorestframework
- psycopg-binary (for PostgreSQL)

### Installation Instructions
1. Clone the repository:
    ```sh
    git clone https://github.com/voboian/Airport-API-Service
    cd airport-api-service
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # for Linux or macOS
    venv\Scripts\activate  # for Windows
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Configure the database in `settings.py`:
```shell
set POSTGRES_HOST=< db_host_name >
set POSTGRES_NAME=< db_name >
set POSTGRES_USER=< db_username >
set POSTGRES_PASSWORD=< password_db >
set SECRET_KEY=< secret_key >
```

5. Run database migrations:
    ```sh
    python manage.py migrate
    ```

### Running the Server
```sh
python manage.py runserver

```
## RUN with Docker

Docker should bу installed

```shell
docker-compose build
```
```shell
docker-compose up
```


# Getting access
 - create user api/user/register/
 - get access token api/user/token/

 - To authenticate, include the obtained token in your request headers with the format:
```shell
 - Authorization: Bearer <your-token>
```

## API Documentation

 - To interact with the API using Swagger, 
 open a web browser and navigate to http://localhost:8000/api/schema/swagger/. 
 Here you will find detailed information about the available endpoints and how to use them.

## Project Features:

- **Information Access Control**: 
Ensures that regular users and administrators have access to appropriate data.
Administrators can access all information, while regular users are restricted to the data they are permitted to see.


- **Airport Information**: 
Provides comprehensive details about airports globally, including their names, codes, nearby major cities.


- **Route Information**: 
Offers data on various flight routes, including the departure and destination airports and the distance between them.


- **Aircraft Information**: 
Supplies details on aircraft, such as their names, types, passenger row configurations, and seat counts per row. 
It also includes functionality for uploading and managing aircraft images.


- **Flight Information**: 
Delivers detailed flight data, including route, departure and arrival times, aircraft details, and seat availability. 
Users can filter flights by departure and arrival dates as well as by source airport name and destination airport name.


- **Order Information**: 
Authenticated users can view and manage their own orders.


- **Ticket Information**: 
Enables the addition of flight tickets to orders, with the ability to specify row and seat numbers.


- **Authentication**: 
Users can create profiles using an email address and password. 
The API uses JWT (JSON Web Tokens) for secure authentication, protecting sensitive flight data.
