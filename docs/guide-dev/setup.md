---
title: Setup
---

## Prerequisites

- git
- docker
- nodejs v20 (you can use nvm to manage node versions)
- yarn



## Get started
### Backend 
1. Clone the repository
    
    ```bash
    git clone git@github.com:unicef/hope.git
    ```
2. go to directory development_tools
    ```bash
    cd hope/development_tools
    ```
3. Create a `.env` file based on the `.env.example` file
    ```bash
    cp .env.example .env
    ```
4. Build the docker image
    ```bash
    docker compose --profile default build
    ```
5. Run initialisation script
    ```bash
    docker compose run --rm backend ./manage.py initdemo
    ```
6. Create a superuser
    ```bash
    docker compose run --rm backend ./manage.py createsuperuser
    ```
6. Run the backend
    ```bash
    docker compose --profile default up
    ```
### Frontend
In a new terminal window
1. Go to the frontend directory
    ```bash
    cd hope/src/frontend
    ```
2. Install dependencies
    ```bash
    yarn
    ```
3. Run the frontend
    ```bash
    yarn dev
    ```
   
## Access the application
- Admin panel is running on `http://localhost:3000/api/unicorn/`
- Login with the superuser credentials created in step 6 of the backend setup
- Select your superuser from list at  `http://localhost:3000/api/unicorn/account/user/`
- Add new User Role at the bottom of the page. Select `Afghanistan` (it has some test data) as the Business Area, and `Role with all Permissions (HOPE)` and save
- Access the frontend on `http://localhost:3000/`
