#!/bin/bash

MARKET_DATA_PRODUCER_PROFILE="market-data-producer"

echo "🚀 Starting the build process for profile: $MARKET_DATA_PRODUCER_PROFILE..."
docker compose --profile $MARKET_DATA_PRODUCER_PROFILE build
if [ $? -eq 0 ]; then
  echo "✅ Build completed successfully for profile: $MARKET_DATA_PRODUCER_PROFILE!"
else
  echo "❌ Build failed for profile: $MARKET_DATA_PRODUCER_PROFILE. Please check the errors above. 💔"
  exit 1
fi

echo "🛑 Shutting down any running containers for profile: $MARKET_DATA_PRODUCER_PROFILE..."
docker compose --profile $MARKET_DATA_PRODUCER_PROFILE down
if [ $? -eq 0 ]; then
  echo "✅ Containers stopped successfully for profile: $MARKET_DATA_PRODUCER_PROFILE! 🧹"
else
  echo "❌ Failed to stop containers for profile: $MARKET_DATA_PRODUCER_PROFILE. Please check for issues. 😢"
  exit 1
fi

echo "🔧 Starting up containers in detached mode for profile: $MARKET_DATA_PRODUCER_PROFILE..."
docker compose --profile $MARKET_DATA_PRODUCER_PROFILE up -d
if [ $? -eq 0 ]; then
  echo "🎉 Containers are up and running for profile: $MARKET_DATA_PRODUCER_PROFILE! 🌟"
  echo "🌐 Visit your application to check if everything is working as expected!"
else
  echo "❌ Failed to start containers for profile: $MARKET_DATA_PRODUCER_PROFILE. Please troubleshoot. 🛠️"
  exit 1
fi

echo "✨ Deployment completed successfully for profile: $MARKET_DATA_PRODUCER_PROFILE! 🎉"