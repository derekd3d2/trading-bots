#!/bin/bash
cd /home/ubuntu/trading-bots

# Show current Git status
echo "📁 Backing up trading-bots repo..."
git status

# Add all modified files
git add .

# Commit with a timestamp
COMMIT_MSG="🗂 Backup: $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# Push to the main branch
git push origin main

# (Optional) tag this backup automatically if env flag is passed
if [[ $1 == "--tag" ]]; then
  TAG_NAME="backup-$(date '+%Y%m%d-%H%M')"
  git tag $TAG_NAME
  git push origin $TAG_NAME
  echo "🔖 Tagged as $TAG_NAME"
fi

echo "✅ Backup complete."
