# revetlla-escape

## Deploy
```
PROJECT_ID="el-teu-projecte"
REGION="europe-southwest1"
SERVICE="tastet-escape-room"

gcloud builds submit --tag \
  "$REGION-docker.pkg.dev/$PROJECT_ID/containers/$SERVICE:latest"
```