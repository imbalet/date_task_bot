#!/bin/sh
set -e

PROJECT_NAME="date_task_bot"

TIMEOUT=60
INTERVAL=5

DEPLOY_LOG="deploy.log"
: > "$DEPLOY_LOG"

OLD_IMAGE=$(docker inspect --format='{{index .Config.Image}}' ${PROJECT_NAME} || echo "")
NEW_IMAGE=$1

if [ -z "$NEW_IMAGE" ]; then
    echo "Usage: $0 <new_image>"
    exit 1
fi

echo "OLD_IMAGE=${OLD_IMAGE}"
echo "NEW_IMAGE=${NEW_IMAGE}"

if [ -n "$OLD_IMAGE" ]; then
    IMAGE=${OLD_IMAGE} docker compose -p ${PROJECT_NAME} down 2>&1 | tee -a "$DEPLOY_LOG" || true
fi

IMAGE=${NEW_IMAGE} docker compose -p ${PROJECT_NAME} up -d --pull missing --force-recreate --quiet-pull 2>&1 | tee -a "$DEPLOY_LOG"

echo "checking health"
elapsed=0
while [ $elapsed -lt $TIMEOUT ]; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$PROJECT_NAME" 2>/dev/null || echo "starting")

    if [ "$STATUS" = "healthy" ]; then
        echo "New container is healthy"

        docker rmi "$OLD_IMAGE" 2>&1 | tee -a "$DEPLOY_LOG" || true

        echo "Success"
        exit 0
    fi

    if [ "$STATUS" = "unhealthy" ]; then
        echo "New container is unhealthy"
        break
    fi

    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
done

echo "New container is unhealthy. Removing new container"

IMAGE=${NEW_IMAGE} docker compose -p ${PROJECT_NAME} down 2>&1 | tee -a "$DEPLOY_LOG" || true

if [ -n "$OLD_IMAGE" ]; then
    echo "Starting old container"
    IMAGE=${OLD_IMAGE} docker compose -p ${PROJECT_NAME} up -d --pull missing --force-recreate --quiet-pull 2>&1 | tee -a "$DEPLOY_LOG"
fi

docker rmi "$NEW_IMAGE" || true

exit 1
