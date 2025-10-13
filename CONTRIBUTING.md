# Contributing to DreamAIry

First off, thank you for considering contributing to DreamAIry! It's people like you that make DreamAIry such a great tool for creating magical stories for children.

## 🌟 Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. By participating, you are expected to uphold this code.

## 🚀 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any alternative solutions you've considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Write clear commit messages**
6. **Submit a pull request**

## 💻 Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Setup Steps

1. **Clone your fork**:
```bash
git clone https://github.com/YOUR_USERNAME/dreamairy.git
cd dreamairy
```

2. **Install backend dependencies**:
```bash
pip install -r backend/requirements.txt
```

3. **Install frontend dependencies**:
```bash
cd frontend
npm install
cd ..
```

4. **Start development servers**:
```bash
# Terminal 1: Backend
python backend/app.py

# Terminal 2: Frontend
cd frontend && npm start
```

## 📝 Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for all functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

Example:
```python
def generate_story_segment(
    context: StoryContext, 
    emotion: EmotionState, 
    goal: EmotionalGoal
) -> StorySegment:
    """
    Generate story segment based on context and emotion.
    
    Args:
        context: Current story context
        emotion: Detected emotion state
        goal: Target emotional goal
        
    Returns:
        Generated story segment
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)

- Use **functional components** with hooks
- Follow **React best practices**
- Use **meaningful component names**
- Keep components **small and reusable**
- Use **PropTypes** or TypeScript for type checking

Example:
```javascript
const StoryArea = ({ 
  sessionId, 
  selectedAge, 
  selectedTheme, 
  onEndSession 
}) => {
  const [storySegments, setStorySegments] = useState([]);
  
  // Component logic here
  
  return (
    <div className="story-area">
      {/* JSX here */}
    </div>
  );
};
```

### Commit Messages

Follow the **Conventional Commits** specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add voice selection to audio controls
fix: resolve audio duplication issue
docs: update README with AWS configuration
refactor: improve story continuity logic
```

## 🧪 Testing

### Running Tests

```bash
# Backend tests
python check_system.py
python test_direct_aws_avatar.py
python test_audio_system.py

# Frontend tests
cd frontend
npm test
```

### Writing Tests

- Write tests for **new features**
- Ensure tests **pass** before submitting PR
- Include **edge cases**
- Test **error handling**

## 📚 Documentation

- Update **README.md** for user-facing changes
- Update **API documentation** for API changes
- Add **inline comments** for complex logic
- Update **CHANGELOG.md** with your changes

## 🔍 Code Review Process

1. **Automated checks** must pass (linting, tests)
2. **At least one maintainer** must review
3. **All comments** must be addressed
4. **Documentation** must be updated
5. **Tests** must be included

## 🎯 Project Structure

Understanding the project structure helps you contribute effectively:

```
dreamairy/
├── backend/           # Python Flask backend
│   ├── admin/         # Admin & AWS integration
│   ├── api/           # API endpoints
│   ├── core/          # Core business logic
│   ├── services/      # Service layer
│   └── models/        # Data models
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # Frontend services
│   │   └── contexts/    # React contexts
├── .kiro/             # Kiro IDE specs
│   └── specs/         # Feature specifications
└── docs/              # Documentation
```

## 🌟 Feature Development Workflow

We use **Spec-Driven Development** for complex features:

1. **Create Spec**: Define requirements in `.kiro/specs/`
2. **Design**: Create design document
3. **Tasks**: Break down into implementation tasks
4. **Implement**: Execute tasks incrementally
5. **Test**: Verify implementation
6. **Document**: Update documentation

## 🐛 Debugging Tips

- Use **logging** extensively
- Check **browser console** for frontend issues
- Check **backend logs** for API issues
- Use **check_system.py** to verify setup
- Test with **both AWS and demo modes**

## 💡 Best Practices

### AWS Integration

- Always provide **fallback** for AWS services
- Handle **content filtering** errors gracefully
- Implement **retry strategies** for transient failures
- Log **AWS service calls** for debugging

### UI/UX

- Maintain **responsive design**
- Ensure **accessibility** (WCAG compliance)
- Provide **loading states**
- Show **error messages** clearly
- Test on **multiple devices**

### Performance

- Optimize **image sizes**
- Minimize **API calls**
- Use **caching** where appropriate
- Lazy load **components**

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: support@dreamairy.com

## 🙏 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **CHANGELOG.md** for their contributions
- **GitHub** contributors page

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to DreamAIry!** 🥷🦸‍♂️✨

*Together, we're creating magical stories for children worldwide* 📚❤️
