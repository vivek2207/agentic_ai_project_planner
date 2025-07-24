# 🤖 AgenticAI Project Planner

An intelligent project planning system built with multi-agent AI frameworks for automated project breakdown, estimation, and resource allocation.

## 🎯 Overview

This repository contains two implementations of an AI-powered project planning system:

1. **CrewAI Implementation** - Original version using OpenAI models
2. **Strands Implementation** - Enhanced version using AWS Bedrock with Claude 4 Sonnet

## 🚀 Features

### Core Capabilities
- **Intelligent Task Breakdown** - AI agents analyze requirements and create detailed task lists
- **Smart Time Estimation** - Realistic hour estimates based on project complexity
- **Resource Allocation** - Optimal team member assignment and timeline planning
- **Sequential Workflow** - Agents build on each other's work for consistency
- **Multi-Format Output** - HTML reports, Markdown files, and structured data

### Advanced Features
- **Model Flexibility** - Support for OpenAI, AWS Bedrock (Claude, Nova Pro)
- **Configurable Agents** - YAML-based agent configuration
- **Comprehensive Logging** - Detailed session logs with timestamps
- **Export Options** - Professional HTML and Markdown reports
- **Adaptive Planning** - Intelligent scope adjustment based on project type

## 📁 Repository Structure

```
├── 📄 L_1.ipynb                    # Original CrewAI notebook implementation
├── 📄 helper.py                    # Environment configuration utilities
├── 📄 requirements.txt             # CrewAI dependencies
├── 📁 config/                      # Agent and task configurations
│   ├── agents.yaml                 # Agent role definitions
│   └── tasks.yaml                  # Task templates
└── 📁 strands-project-planner/     # Enhanced Strands implementation
    ├── 📄 main.py                  # Main execution script
    ├── 📄 aws_config.py            # AWS Bedrock configuration
    ├── 📄 models.py                # Pydantic data models
    ├── 📄 workflow_tracker.py      # Sequential workflow management
    ├── 📄 logger_config.py         # Logging system
    ├── 📄 output_formatter.py      # Report generation
    ├── 📄 requirements.txt         # Strands dependencies
    ├── 📁 config/                  # Configuration files
    ├── 📁 outputs/                 # Generated reports
    └── 📁 logs/                    # Session logs
```

## 🛠️ Quick Start

### CrewAI Implementation

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run Notebook**
   ```bash
   jupyter notebook L_1.ipynb
   ```

### Strands Implementation (Recommended)

1. **Setup Environment**
   ```bash
   cd strands-project-planner
   pip install -r requirements.txt
   ```

2. **Configure AWS**
   ```bash
   # Copy template and add your AWS credentials
   cp .env.template .env
   # Edit .env with your AWS credentials
   ```

3. **Run the System**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### AWS Bedrock Models Supported
- **Claude 4 Sonnet** - `us.anthropic.claude-sonnet-4-20250514-v1:0` (Default)
- **Claude 3.5 Sonnet** - `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Claude 3 Sonnet** - `anthropic.claude-3-sonnet-20240229-v1:0`
- **Nova Pro** - `us.amazon.nova-pro-v1:0`

### Agent Configuration

The system uses three specialized agents:

1. **Project Planning Agent** - Breaks down requirements into tasks
2. **Estimation Agent** - Provides time and resource estimates
3. **Resource Allocation Agent** - Optimizes team assignments and creates milestones

## 📊 Sample Output

### Project Summary
- **Total Tasks**: 8-15 (adaptive based on complexity)
- **Total Effort**: 120-400 hours (realistic estimates)
- **Duration**: 3-8 weeks (including dependencies)
- **Team**: 5 members with specialized roles

### Generated Reports
- **HTML Report**: Professional formatted report with styling
- **Markdown Report**: Clean text format for documentation
- **Structured Data**: JSON/Pydantic models for integration

## 🎛️ Customization

### Project Types Supported
- **Simple Websites** - 3-4 weeks, 120-160 hours
- **E-commerce Platforms** - 6-8 weeks, 200-400 hours
- **Enterprise Applications** - 12+ weeks, 500+ hours

### Extending the System
1. **Add New Models** - Update `aws_config.py` with new model mappings
2. **Custom Agents** - Modify `config/agents.yaml` for different roles
3. **New Output Formats** - Extend `output_formatter.py`
4. **Different Workflows** - Update `workflow_tracker.py`

## 🔧 Advanced Features

### Sequential Workflow Validation
- Ensures Agent 2 uses exact tasks from Agent 1
- Agent 3 builds on specific estimates from Agent 2
- Validates complete task → estimate → allocation chain

### Intelligent Parsing
- Extracts agent reasoning vs. hardcoded templates
- Adapts to different project complexities
- Handles various output formats gracefully

### Production Ready
- Comprehensive logging with timestamps
- Error handling and validation
- Configurable for different environments

## 🚦 Getting Started Examples

### Simple Website Project
```python
project_type = 'Small Business Website'
project_objectives = 'Professional online presence'
# Expected: ~8 tasks, ~140 hours, ~4 weeks
```

### Complex Application
```python
project_type = 'E-commerce Platform'
project_objectives = 'Full-featured online store'
# Expected: ~15 tasks, ~350 hours, ~8 weeks
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test both implementations
4. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙋‍♂️ Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the logs in `strands-project-planner/logs/`
- Review sample outputs in `strands-project-planner/outputs/`

---

**Built with ❤️ using CrewAI and AWS Strands frameworks** 