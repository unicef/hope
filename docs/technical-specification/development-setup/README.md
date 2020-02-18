# Development Setup / Process

## Local Setup

1. Install [Docker](https://docs.docker.com/engine/installation/) for your OS.
2. Receive .env file from your team member. There are AD secrets there.
3. Run 

```bash
docker-compose build
docker-compose up
docker-compose exec backend bash
# in docker container
./manage.py reset_db
./manage.py migrate
./manage.py loadbusinessareas
./manage.py generatefixtures 
./manage.py collectstatic 
```

Access the frontend in your browser at `localhost:8082/login` . Backend can be accessed at `/api/` i.e. `localhost:8082/api/admin/` 



## Development / Build / Deployment Process

![Engineering Process](../../.gitbook/assets/unicef_hct-mis__online_whiteboard_for_visual_collaboration%20%281%29.jpg)

## Git Branching

![Git Branching Model](../../.gitbook/assets/unicef_hct-mis__online_whiteboard_for_visual_collaboration.jpg)



