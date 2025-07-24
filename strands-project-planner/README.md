# Strands Project Planner

A project planning system built with AWS Strands framework and Bedrock models.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS**
   - Copy `.env.template` to `.env`
   - Add your AWS credentials
   - Ensure Bedrock access is enabled in your AWS account

3. **Run the System**
   ```bash
   python main.py
   ```

## Features

- **Planning Agent**: Breaks down project requirements into tasks
- **Estimation Agent**: Provides time and resource estimates  
- **Allocation Agent**: Optimizes resource allocation and creates project plan

## Models Supported

- Claude 3 Sonnet
- Claude 3.5 Sonnet  
- Amazon Nova Pro

## Output

The system generates structured project plans with:
- Detailed task breakdown with time estimates
- Resource requirements for each task
- Project milestones and timelines 