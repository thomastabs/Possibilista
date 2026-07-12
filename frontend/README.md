# Possibilista Frontend

This directory contains the Next.js frontend package and its Dockerfile.

## Docker build

Build the frontend image from the repository root:

```bash
./build_frontend_docker.sh
```

The script builds `possibilista-frontend:latest` from `./frontend`.

Before invoking Docker, the script checks that `frontend/Dockerfile` exists. If the Dockerfile is missing or misnamed, the script exits with a non-zero status and prints a clear error telling you where the Dockerfile is expected.
