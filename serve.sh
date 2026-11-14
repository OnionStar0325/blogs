#!/usr/bin/env bash
# Local Jekyll Development Server
# Automatically overrides cdn_url to /assets/images for instant local image preview

echo "🚀 Starting Jekyll Local Development Server..."
echo "📂 Loaded config: _config.yml, _config_dev.yml (Local Assets Mode)"
echo "🌐 Local address: http://localhost:4000/ or http://100.126.81.56:4000/"

bundle exec jekyll serve --host 0.0.0.0 --port 4000 --config _config.yml,_config_dev.yml "$@"
