# Contributing to Raspberry Pi Media Player

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in the [Issues](https://github.com/Kaiden-Buchter/raspberry-pi-media-player/issues) section
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Raspberry Pi model, OS version, Python version)
   - Relevant logs or screenshots

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git
   cd raspberry-pi-media-player
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   - Test on actual Raspberry Pi hardware if possible
   - Verify existing functionality still works
   - Run `python3 test_setup.py` to verify setup

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a PR on GitHub

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Comments
- Write clear, concise comments
- Explain "why" not "what" when the code is complex
- Update comments when changing code

### Configuration
- Use YAML for configuration files
- Provide sensible defaults
- Document all configuration options

## Development Setup

1. Install development dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set up test configuration:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml for testing
   ```

## Testing

- Test on Raspberry Pi 5 when possible
- Test with various media formats (HEIC, MP4, MOV, etc.)
- Verify Google Drive sync functionality
- Check performance with large media libraries

## Areas for Contribution

We welcome contributions in these areas:

### Features
- Additional video format support
- More transition effects
- Playlist management
- Remote control via web interface
- Multiple monitor support
- Audio playback support

### Performance
- Optimization for smoother playback
- Reduced memory usage
- Faster sync operations

### Documentation
- Improve installation instructions
- Add more troubleshooting scenarios
- Translate documentation
- Create video tutorials

### Testing
- Automated testing framework
- Unit tests for core functions
- Integration tests

### Bug Fixes
- Fix reported issues
- Improve error handling
- Add validation

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing discussions
- Review the README.md for documentation

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the project's goals

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Raspberry Pi Media Player!
