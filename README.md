# IR code - Neville Longbottom

## Docker Submissions

To create a new docker submission, first create a new subdirectory in `runs` and create a Dockerfile and a python script (p.e. `main.py`). For reference you can use the `baseline` folder. Next you have to add a service for your run in the `docker-compose.yml` inside this root directory. You can copy the baseline service but you have to change the image name and build dockerfile path. 

To build all containers, run `docker compose build`.

To push all images to the tira remote, run `docker compose push`.
