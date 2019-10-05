# Development Setup / Process

## Local Setup

1. Install [Docker](https://docs.docker.com/engine/installation/) for your OS. Also install Fabric via `pip install fabric`
2. Create .env file with the reference of`.env.example`or receive .env file from your team member.
3. Run `fab compose` to create docker images and start all services. Django static collections and migrations are also run as part of this process.
4. Access the frontend in your browser at `localhost:8082` . Backend can be accessed at `/api/` i.e. `localhost:8082/api/admin/` 



## Development / Build / Deployment Process

![Engineering Process](../../.gitbook/assets/unicef_hct-mis__online_whiteboard_for_visual_collaboration%20%281%29.jpg)

## Git Branching

![Git Branching Model](../../.gitbook/assets/unicef_hct-mis__online_whiteboard_for_visual_collaboration.jpg)



