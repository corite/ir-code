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

