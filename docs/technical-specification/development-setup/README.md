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

Access the frontend in your browser at [`localhost:8082/login`](http://localhost:8082/login) . 

Backend can be accessed at `/api/` i.e. [`localhost:8082/api/admin/`](http://localhost:8082/api/admin/) 



## Development / Build / Deployment Process

![](../../.gitbook/assets/unicef-hct-mis-1.jpg)

## Git Branching / Cloud environments

Below represents approximately strategy we hope to follow. We may or may not use tags in the master branch \(tbd\). Additionally instead of release branches \(since HCT is under development\) we may use a staging branch approach \(more stable than develop\).

![Git Branching Model](../../.gitbook/assets/unicef_hct-mis__online_whiteboard_for_visual_collaboration.jpg)

The following are the code branches and their CI / CD usage.

| Branch | Auto-deployed? | Cloud environment |
| :--- | :--- | :--- |
| develop | yes | [https://dev-hct.unitst.org/](https://dev-hct.unitst.org/afghanistan/) |
| staging | yes | [https://staging-hct.unitst.org/](https://staging-hct.unitst.org/) |
| master | no | ? |
| feature/\* or bug/\* | no | n/a |

In the future hotfix branches might be made as well which merge directly to master potentially. A UAT environment that mirrors the stability of production \(master branch\) might be necessary as well. If strictly following an agile methodology, it may or may not be necessary, but a UAT env mirroring production might be helpful for production focused hot fix testing.

