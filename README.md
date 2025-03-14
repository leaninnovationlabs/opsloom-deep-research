# README
Opsloom provides a way to build out a custom AI agent that can be used to automate tasks within your enterprise and build out various AI assistants. It provies out the box that is responsive and can be easily embedded into your existing applications. Opsloom also provides a way to build out custom assistants that are more domain specific and can be used to automate tasks within your enterprise.

# Local Dev Environment Setup
Using env.example as a reference, create a .env file and include all keys and environment variables.
You will use this file as an argument to the Docker command which runs the application.

## 1. Setup Python Environment

We are using uv for package management.

`https://docs.astral.sh/uv/#getting-started`

install for Mac/Linux with this command: https://docs.astral.sh/uv/#getting-started

uv automatically creates a virtual environment when running certain commands. To install the dependencies in pyproject.toml in the virtual environment, please run

```
    uv sync
```

## 2. Running Database Locally
Opsloom works out of the box utilizing postgres as the database. It utilizes database to store the user data and the conversation data. Opsloom also provides some examples on how to use Postgres as the vector database to store the embeddings.

    1. Ensure that you have a Postgres container with pgvector running . 
        
    You can use the script in db/start_postgres.sh will start one for you or you can use an external AWS RDS. You can configure the default username and password in the .sh file

    ```bash
        sh db/start_postgres.sh
    ```

    2. Run initial set of database script using alembic

    This will run all the scripts under the db folder. The Postgres connection string is read from .env

    ```bash
        uv run alembic upgrade head
    ```

## 3. Run backend server
Run python fast api server using the following command

```bash
    uv sync 
    uv run uvicorn server:app --reload --port 8080
```

Once you have the backend server running you can invoke the backend APIs by launching Bruno and loading the /docs/api_docs folder


## 3. Run frontend server

Run vite server using the following command

```bash
    cd frontend
    npm i
    npm run dev
```


## Run docs server (optional)

Run the docs server using the following command
```bash
npm i
npm run docs:dev
```
-------------------

# Database Migrations Scripts

1. Steps to follow to create a new database script

    To create a new script you can either run the following or copy an existing file and rename it
    ```
        uv run alembic revision -m "create account table"
    ```

2. Downgrade a version

    To downgrade a version you can run the following command, this will downgrade the database by 1 version

    ```
    uv run alembic downgrade -1
    ```


-------------------

# Run using Docker

To run the app as a Docker container locally:

1. Build out the docker image for opsloom

    ```
      # This will create a docker image opsloom
      ./infra/scripts/build_app.sh
    ```

2. Run the database and docker images 

    This will start the db, run the migration scripts and start the opsloom container
    ```bash
        docker compose up
    ```
    ** Note: You can update the docker docker compose file as needed for the userid and passwords**

### Alternatively you can use docker commands individually
3a. Start the database container
    ```bash
        ./infra/scripts/start_db.sh
    ```

3a. Run the docker image to do the db upgrade
    **Note: Make sure .env.docker is configured properly, similar to env but no quotes or spaces**
    ```bash
        docker run --env-file .env.docker -w /app opsloom sh -c "uv run alembic upgrade head;"
    ```

3b. Start the opsloom container
    **Note: Make sure .env.docker is configured properly, similar to env but no quotes or spaces**
    ```bash
        docker run -d --env-file .env.docker --name opsloom -p 8080:8080 opsloom
    ```

-------------------

# Trouble shooting 
1. If you get error with psycopg2, you can install the binary version using the following command

    ```
      pip install "psycopg[binary]"
    ```

2. Get the Icons from using the following link

    [Google Fonts](https://fonts.google.com/icons?selected=Material+Symbols+Outlined:support_agent:FILL@0;wght@400;GRAD@0;opsz@24&icon.query=car&icon.size=24&icon.color=%235f6368)