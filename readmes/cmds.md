## Presidio Complete Guide: Commands & JSON Output

### 1. Local testing (individual service)

- **Dockerfile**: `Dockerfile.presidio-scan`
- **Compose file**: `docker-compose.yml`
- **Usage**: Used for local testing of the individual `presidio-scan` service.

- **Run scan container**:

```sh
docker compose run --rm \
  -v /home/ayush/Desktop/security-tools/presidio/scan-entities/:/data \
  presidio-scan python presidio-scan.py /data/ \
  --analyze-url http://presidio-analyzer:5001/analyze \
  --output /data/sample_pdf_result_all.json
```

- **Build steps**:
  - **Update**: `.env`
  - **Build image**:

```sh
docker compose build
```

### 2. All-in-one image (merged services)

- **Dockerfile**: `Dockerfile.all-in-one`
- **Entrypoint**: `entrypoint-all.sh`
- **Usage**: Merge all Presidio services into a single container.

- **Run all-in-one scan**:

```sh
docker run --rm \
  -v /home/ayush/Desktop/security-tools/presidio/scan-entities/:/data \
  ayush1136/presidio-all:latest scan /data \
  --output /data/scan_all_entites.json
```

- **Build image**:

```sh
docker build -f Dockerfile.all-in-one -t <image-name> .
```