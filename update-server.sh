#!/bin/bash

# --- Configuration ---
# Define paths to avoid hardcoded relative paths
SERVER_DIR="/home/hoag/Documents/toto/minecraft/labo"
FERIUM_BIN="$SERVER_DIR/ferium"
JAR_NAME="fabric-server-launch.jar"
SERVICE_NAME="minecraft-saladia.service"

# Input version from Python bot
VERSION=$1

# Exit immediately if a command exits with a non-zero status
set -e

# --- Functions ---
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# --- Pre-flight checks ---
if [ -z "$VERSION" ]; then
    log "ERROR: No version provided."
    exit 1
fi

if ! command -v jq &> /dev/null; then
    log "ERROR: jq is not installed."
    exit 1
fi

# --- Fabric API Metadata ---
log "Checking Fabric availability for version $VERSION..."
META_DATA=$(curl -s "https://meta.fabricmc.net/v2/versions/loader/$VERSION")

if [ "$META_DATA" == "[]" ] || [ -z "$META_DATA" ]; then
    log "ERROR: Fabric is not available for Minecraft $VERSION."
    exit 1
fi

# Extracting versions using jq
LOADER_VERSION=$(echo "$META_DATA" | jq -r '.[0].loader.version')
INSTALLER_VERSION=$(curl -s https://meta.fabricmc.net/v2/versions/installer | jq -r '.[0].version')

log "Latest Loader: $LOADER_VERSION | Installer: $INSTALLER_VERSION"

# --- Maintenance Cycle ---
log "Stopping $SERVICE_NAME..."
sudo systemctl stop "$SERVICE_NAME"

# Download the new server JAR
JAR_URL="https://meta.fabricmc.net/v2/versions/loader/$VERSION/$LOADER_VERSION/$INSTALLER_VERSION/server/jar"
log "Downloading server JAR from: $JAR_URL"

wget -4 -q -O "$SERVER_DIR/$JAR_NAME" "$JAR_URL"

# --- Mod Management (Ferium) ---
log "Updating mods via Ferium..."
# Ensure we are in the right directory or use absolute paths for config
"$FERIUM_BIN" profile configure --game-version "$VERSION"
"$FERIUM_BIN" upgrade

# --- Restart ---
log "Starting $SERVICE_NAME..."
sudo systemctl start "$SERVICE_NAME"

log "Upgrade to $VERSION completed successfully."