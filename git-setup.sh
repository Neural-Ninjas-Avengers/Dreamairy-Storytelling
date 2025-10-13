#!/bin/bash

# DreamAIry - Git Repository Setup Script
# This script initializes the Git repository and prepares it for GitHub

echo "🚀 Setting up DreamAIry Git repository..."

# Initialize git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "feat: initial commit - DreamAIry adaptive storytelling application

- Add React-based storytelling interface
- Implement AI-powered story generation system
- Add photo integration for personalized stories
- Include emotion detection capabilities
- Support multi-language interface (Spanish/English)
- Implement premium glassmorphism UI design
- Add responsive mobile-first design
- Include audio narration with text-to-speech
- Add AI image generation with SVG fallbacks
- Implement comprehensive fallback systems
- Add project documentation and setup guides"

echo "✅ Initial commit created successfully!"

echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Copy the repository URL"
echo "3. Run the following commands:"
echo ""
echo "   git remote add origin https://github.com/Neural-Ninjas-Avengers/dreamairy-storytelling.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🌟 Your DreamAIry project is ready for GitHub!"

# Make the script executable
chmod +x git-setup.sh