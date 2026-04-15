Mini Project 2 — Event Planner API

This project is for SFWE477 Backend Development with FastAPI course. In this project, I built a FastAPI application and connected it to a MongoDB database using Beanie.

In Mini Project 1, we were using in-memory data, but in this project I used a real database, so the data is saved permanently and does not disappear when the application restarts.

The application has two main parts: Events and Users. Users can sign up and sign in. Events can be created, updated, deleted, and listed using API endpoints.

I used FastAPI for the backend, MongoDB as the database, and Beanie as the ODM. I also used Motor for async database operations.

The project is structured with separate folders like models, routes, and database. I created a Database class to handle all CRUD operations instead of writing database logic directly inside the routes.

To run the project, first I created a virtual environment and installed the required packages. Then I started MongoDB locally and created a .env file for the database connection. After that, I ran the project using uvicorn and tested the endpoints using Swagger.
# README.md part B
Q1 — Why mongo and not localhost?
Each container has its own network namespace. If the app container runs inside localhost, it points to that container, not the mongo container. Docker Compose connects services on its own private network, and service names (mongo) function like DNS.

Q2 — What does `depends_on` do?
`depends_on` controls the startup order. The app container will not attempt to start until the mongo container is running. However, this does not mean that MongoDB is ready to accept connections. For real assurance, you need to use `healthcheck` and `condition: service_healthy`.

Q3 — What is the purpose of a volume?
A volume maps the data on the host to `/data/db` inside the container. This ensures that the MongoDB data persists even if the container is restarted. If there is no volume, the container's file system is erased and the data is lost when docker compose is down.

Q4 — Why is `requirements.txt` copied first?
Docker caches each layer. Copying requirements.txt first and then running pip install ensures that this cumbersome process only runs again when the dependencies change. When the code changes, only the subsequent layers are rebuilt; the package installation is not repeated.