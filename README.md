# IR code - Neville Longbottom

## Docker Submissions

To create a new docker submission, first create a new subdirectory in `runs` and create a Dockerfile and a python script (p.e. `main.py`). For reference you can use the `baseline` folder. Next you have to add a build&push task in the `.github/workflows/deploy.yml` like this, substituting run with your run name:

```yaml
      - name: Build and push [run]
        uses: docker/build-push-action@v3
        with:
          context: .
          file: ./runs/[run]/Dockerfile
          push: true
          tags: registry.webis.de/code-research/tira/tira-user-touche23-neville-longbottom/[run]:latest
```

Push your changes to the github repo and the new container will be built and deployed after your changes hae been merged into the main branch.

## Running locally

```
docker build -t neville -f submission/Dockerfile .
docker run --rm \
	--mount type=bind,source="$(pwd)"/cache,target=/cache \
        --mount type=bind,source="$(pwd)"/out,target=/out \
        --mount type=bind,source="$(pwd)"/in,target=/in \
        neville bash -c 'DEBATER_TOKEN="my_api_token" TIRA_INPUT_DIRECTORY="/in/sample-input/full-rank" TIRA_OUTPUT_DIRECTORY="/out" ./main.py'
```
