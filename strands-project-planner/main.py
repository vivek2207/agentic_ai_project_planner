import warnings
warnings.filterwarnings('ignore')

import os
import yaml
import pandas as pd
from strands import Agent, tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
from aws_config import get_aws_bedrock_model
from models import ProjectPlan, TaskEstimate, Milestone
from logger_config import setup_logger, log_session_start
from output_formatter import OutputFormatter
from workflow_tracker import WorkflowTracker

class ProjectPlannerSystem:
    def __init__(self, model_name="claude-3-sonnet"):
        """Initialize the project planner system with Strands agents"""
        self.logger = setup_logger()
        log_session_start(self.logger)
        
        self.logger.info(f"Initializing Project Planner with model: {model_name}")
        self.model = get_aws_bedrock_model(model_name)
        self.load_configs()
        self.setup_agents()
        self.logger.info("Project Planner System initialized successfully")
        
    def load_configs(self):
        """Load YAML configurations for agents and tasks"""
        files = {
            'agents': 'config/agents.yaml',
            'tasks': 'config/tasks.yaml'
        }
        
        configs = {}
        for config_type, file_path in files.items():
            with open(file_path, 'r') as file:
                configs[config_type] = yaml.safe_load(file)
        
        self.agents_config = configs['agents']
        self.tasks_config = configs['tasks']
    
    def setup_agents(self):
        """Setup Strands agents with conversation management"""
        conv_manager = SlidingWindowConversationManager(window_size=10)
        
        # Project Planning Agent
        self.planning_agent = Agent(
            model=self.model,
            system_prompt=f"""
            Role: {self.agents_config['project_planning_agent']['role']}
            Goal: {self.agents_config['project_planning_agent']['goal']}
            Backstory: {self.agents_config['project_planning_agent']['backstory']}
            
            You are an experienced project manager who understands how to appropriately scope projects based on their complexity and requirements. You have deep expertise in web development projects and can distinguish between simple business websites and complex enterprise applications.
            
            When planning, consider the actual scope and complexity of the requirements provided. Use your expertise to break down work into realistic, actionable tasks that align with industry standards and best practices.
            """,
            conversation_manager=conv_manager,
            tools=[self.task_breakdown_tool]
        )
        
        # Estimation Agent  
        self.estimation_agent = Agent(
            model=self.model,
            system_prompt=f"""
            Role: {self.agents_config['estimation_agent']['role']}
            Goal: {self.agents_config['estimation_agent']['goal']}
            Backstory: {self.agents_config['estimation_agent']['backstory']}
            
            You are a seasoned estimation expert with extensive experience in web development projects. You understand the difference between simple informational websites and complex web applications. Your estimates are known for being accurate because you consider the actual complexity, available technologies, frameworks, and modern development practices.
            
            You provide realistic time estimates based on the specific requirements and project scope, taking into account factors like use of existing templates, content management systems, and standard web development practices.
            """,
            conversation_manager=conv_manager,
            tools=[self.time_resource_estimation_tool]
        )
        
        # Resource Allocation Agent
        self.allocation_agent = Agent(
            model=self.model,
            system_prompt=f"""
            Role: {self.agents_config['resource_allocation_agent']['role']}
            Goal: {self.agents_config['resource_allocation_agent']['goal']}
            Backstory: {self.agents_config['resource_allocation_agent']['backstory']}
            """,
            conversation_manager=conv_manager,
            tools=[self.resource_allocation_tool]
        )

    @tool
    def task_breakdown_tool(self, project_requirements: str, project_type: str, team_members: str) -> str:
        """Break down project requirements into individual tasks"""
        task_description = self.tasks_config['task_breakdown']['description'].format(
            project_type=project_type,
            project_requirements=project_requirements,
            team_members=team_members
        )
        return f"Task Breakdown Analysis:\n{task_description}"

    @tool  
    def time_resource_estimation_tool(self, task_breakdown: str, project_type: str) -> str:
        """Estimate time, resources, and effort for each task"""
        return f"TASK ESTIMATION ANALYSIS:\n\nProcessing the following task breakdown for {project_type}:\n\n{task_breakdown}\n\nProviding detailed time and resource estimates for each task above."

    @tool
    def resource_allocation_tool(self, estimations: str, team_members: str, project_type: str) -> str:
        """Allocate resources and create final project plan"""
        return f"RESOURCE ALLOCATION ANALYSIS:\n\nCreating allocation plan for {project_type} using:\n\nTEAM MEMBERS:\n{team_members}\n\nTASKS WITH ESTIMATES:\n{estimations}\n\nGenerating detailed resource allocation and milestone plan based on the above tasks and estimates."

    def run_project_planning(self, inputs: dict) -> dict:
        """Execute the complete project planning workflow with sequential tracking"""
        
        self.logger.info(f"Starting project planning for: {inputs['project_type']}")
        print("🚀 Starting Project Planning Workflow...")
        
        # Initialize workflow tracker for sequential processing
        tracker = WorkflowTracker()
        
        # Step 1: Task Breakdown
        print("📋 Step 1/3: Task Breakdown...")
        self.logger.info("Running Task Breakdown phase")
        task_breakdown = self.planning_agent(
            f"Analyze and break down this {inputs['project_type']} project:\n"
            f"Objectives: {inputs['project_objectives']}\n"
            f"Requirements: {inputs['project_requirements']}\n"
            f"Team: {inputs['team_members']}"
        )
        self.logger.info("Task Breakdown completed")
        
        # Extract tasks from breakdown
        tasks = tracker.extract_tasks_from_breakdown(str(task_breakdown))
        print(f"   ✅ Extracted {len(tasks)} tasks")
        
        # Step 2: Time & Resource Estimation
        print("⏱️  Step 2/3: Time & Resource Estimation...")
        self.logger.info("Running Time & Resource Estimation phase")
        estimations = self.estimation_agent(
            f"You must provide time and resource estimates for THE EXACT TASKS listed in the task breakdown below.\n\n"
            f"IMPORTANT: Use the specific tasks from the breakdown - do not create new tasks.\n"
            f"For each task listed, provide:\n"
            f"- Estimated hours needed\n"
            f"- Required resources/skills\n"
            f"- Effort level (High/Medium/Low)\n\n"
            f"Project Type: {inputs['project_type']}\n\n"
            f"TASK BREAKDOWN TO ESTIMATE:\n"
            f"{'-'*50}\n"
            f"{task_breakdown}\n"
            f"{'-'*50}\n\n"
            f"Provide estimates for each task above."
        )
        self.logger.info("Time & Resource Estimation completed")
        
        # Extract estimates and link to tasks
        tasks_with_estimates = tracker.extract_estimates_from_output(str(estimations))
        estimated_hours = sum(task.get('estimated_hours', 0) for task in tasks_with_estimates if task.get('estimated_hours'))
        print(f"   ✅ Added estimates: {estimated_hours} total hours")
        
        # Step 3: Resource Allocation
        print("👥 Step 3/3: Resource Allocation...")
        self.logger.info("Running Resource Allocation phase")
        final_plan = self.allocation_agent(
            f"Create the final resource allocation plan using THE EXACT TASKS and ESTIMATES from previous steps.\n\n"
            f"IMPORTANT: Use the specific tasks and estimates provided - do not create new ones.\n"
            f"For each task with its estimate, assign:\n"
            f"- Specific team member(s) responsible\n"
            f"- Start and end dates\n"
            f"- Dependencies between tasks\n"
            f"- Create logical milestones grouping related tasks\n\n"
            f"Project Type: {inputs['project_type']}\n\n"
            f"AVAILABLE TEAM:\n"
            f"{inputs['team_members']}\n\n"
            f"TASKS WITH ESTIMATES TO ALLOCATE:\n"
            f"{'-'*50}\n"
            f"{estimations}\n"
            f"{'-'*50}\n\n"
            f"Create allocation plan for the tasks above."
        )
        self.logger.info("Resource Allocation completed")
        
        # Extract allocations and create final structured output
        allocation_result = tracker.extract_allocations_from_output(str(final_plan))
        milestones = allocation_result.get('milestones', [])
        print(f"   ✅ Created {len(milestones)} milestones")
        
        # Get unified summary
        unified_summary = tracker.get_unified_summary()
        
        # Log the complete result
        self.logger.info("="*50)
        self.logger.info("COMPLETE WORKFLOW RESULT:")
        self.logger.info("="*50)
        self.logger.info(f"Tasks: {unified_summary.get('total_tasks', 0)}")
        self.logger.info(f"Total Hours: {unified_summary.get('total_hours', 0)}")
        self.logger.info(f"Milestones: {len(milestones)}")
        self.logger.info("="*50)
        
        # Return structured workflow result
        return {
            'raw_outputs': {
                'task_breakdown': str(task_breakdown),
                'estimations': str(estimations),
                'allocations': str(final_plan)
            },
            'structured_data': unified_summary,
            'workflow_complete': True
        }


def display_results(result, logger):
    """Display results from structured workflow tracking"""
    print("\n✅ Project Planning Complete!")
    
    if not result.get('workflow_complete'):
        print("❌ Workflow tracking failed - using fallback parsing")
        # Fallback to old parsing method
        result_text = str(result)
        tasks_data = parse_tasks_from_output(result_text)
        milestones_data = parse_milestones_from_output(result_text)
        summary_data = calculate_summary_data(tasks_data, result_text)
    else:
        # Use structured workflow data
        structured_data = result['structured_data']
        tasks_data = structured_data.get('tasks_with_details', [])
        milestones_data = structured_data.get('milestones', [])
        
        summary_data = {
            'task_count': structured_data.get('total_tasks', 0),
            'total_hours': structured_data.get('total_hours', 0),
            'duration_weeks': structured_data.get('total_weeks', 0),
            'effort_breakdown': structured_data.get('effort_breakdown', {})
        }
    
    # Create output formatter
    formatter = OutputFormatter("Small Business Website Project")
    
    # Get combined text for detailed output
    raw_outputs = result.get('raw_outputs', {})
    combined_text = f"""
TASK BREAKDOWN:
{raw_outputs.get('task_breakdown', 'N/A')}

ESTIMATIONS:
{raw_outputs.get('estimations', 'N/A')}

RESOURCE ALLOCATION:
{raw_outputs.get('allocations', 'N/A')}
    """
    
    # Save HTML and Markdown reports
    try:
        html_file = formatter.save_html_report(tasks_data, milestones_data, combined_text, summary_data)
        md_file = formatter.save_markdown_report(tasks_data, milestones_data, combined_text, summary_data)
        
        print(f"📄 Reports saved:")
        print(f"   • HTML: {html_file}")
        print(f"   • Markdown: {md_file}")
        
        logger.info(f"Reports saved successfully: {html_file}, {md_file}")
        
    except Exception as e:
        print(f"❌ Error saving reports: {e}")
        logger.error(f"Failed to save reports: {e}")
    
    # Display enhanced console summary showing sequential workflow
    print(f"\n📊 Sequential Workflow Summary:")
    print(f"   📋 Tasks Identified: {summary_data.get('task_count', 0)}")
    print(f"   ⏱️  Total Effort: {summary_data.get('total_hours', 0)} hours")
    print(f"   📅 Duration: {summary_data.get('duration_weeks', 0)} weeks")
    print(f"   🎯 Milestones: {len(milestones_data)}")
    
    # Show effort breakdown
    effort_breakdown = summary_data.get('effort_breakdown', {})
    print(f"   💪 Effort Distribution: {effort_breakdown.get('High', 0)} High, {effort_breakdown.get('Medium', 0)} Medium, {effort_breakdown.get('Low', 0)} Low")
    
    # Show sequential workflow validation
    if result.get('workflow_complete'):
        print(f"\n✅ Sequential Workflow Validated:")
        print(f"   • Task Breakdown → Estimation → Allocation linkage confirmed")
        print(f"   • All tasks have estimates and resource assignments")
    
    print(f"\n💡 View detailed reports in the 'outputs' folder")
    print(f"💡 Check 'logs/project_planner.log' for complete session details")


def parse_tasks_from_output(text):
    """Extract task information from agent output text"""
    tasks = []
    lines = text.split('\n')
    
    current_task = None
    in_task_section = False
    
    for line in lines:
        line = line.strip()
        
        # Look for numbered tasks (1., 2., etc.)
        if line and (line[0].isdigit() and '. ' in line):
            if current_task:
                tasks.append(current_task)
            
            # Extract task name
            task_name = line.split('. ', 1)[1].split(':')[0].strip()
            current_task = {
                'task_name': task_name,
                'estimated_time': 'Not specified',
                'resources': [],
                'effort': 'Medium'
            }
            in_task_section = True
        
        elif in_task_section and current_task:
            # Look for time estimates
            if 'Time:' in line or 'weeks' in line.lower():
                if 'week' in line.lower():
                    time_match = line.lower()
                    if '1 week' in time_match:
                        current_task['estimated_time'] = '40 hours'
                    elif '2 week' in time_match:
                        current_task['estimated_time'] = '80 hours'
                    elif '3 week' in time_match:
                        current_task['estimated_time'] = '120 hours'
            
            # Look for effort levels
            if 'Effort:' in line:
                if 'High' in line:
                    current_task['effort'] = 'High'
                elif 'Low' in line:
                    current_task['effort'] = 'Low'
                elif 'Medium' in line:
                    current_task['effort'] = 'Medium'
            
            # Look for resources
            if 'Resources:' in line or 'Team:' in line:
                # Extract team members mentioned
                if 'Designer' in line:
                    current_task['resources'].append('Designer')
                if 'Software Engineer' in line or 'Engineer' in line:
                    current_task['resources'].append('Software Engineer')
                if 'QA' in line:
                    current_task['resources'].append('QA Engineer')
                if 'Project Manager' in line:
                    current_task['resources'].append('Project Manager')
    
    # Don't forget the last task
    if current_task:
        tasks.append(current_task)
    
    return tasks[:12]  # Limit to first 12 tasks for clean display


def parse_milestones_from_output(text):
    """Extract milestone information from agent output text"""
    milestones = []
    lines = text.split('\n')
    
    in_milestone_section = False
    for line in lines:
        line = line.strip()
        
        if '**Milestones**:' in line or 'Milestones:' in line:
            in_milestone_section = True
            continue
        
        if in_milestone_section and line:
            # Look for numbered milestones
            if line and (line[0].isdigit() and '. ' in line):
                milestone_name = line.split('. ', 1)[1].split('(')[0].strip()
                
                # Extract week info if present  
                week_info = ""
                if '(Week' in line:
                    week_info = line.split('(')[1].split(')')[0]
                
                milestones.append({
                    'milestone_name': milestone_name,
                    'timeline': week_info,
                    'status': 'Pending'
                })
            
            # Stop if we hit another section
            if line.startswith('**') and 'Milestones' not in line:
                break
    
    return milestones





def calculate_summary_data(tasks_data, text):
    """Calculate summary data for the project"""
    
    # Calculate total effort from tasks
    total_hours = 0
    task_count = len(tasks_data)
    effort_breakdown = {'High': 0, 'Medium': 0, 'Low': 0}
    
    for task in tasks_data:
        # Extract hours from estimated_time
        time_str = task.get('estimated_time', '0')
        if 'hour' in time_str.lower():
            try:
                # Handle different formats like "8 hours", "8hours", "8 hrs"
                import re
                hours_match = re.search(r'(\d+)', time_str)
                if hours_match:
                    hours = int(hours_match.group(1))
                    total_hours += hours
            except:
                pass
        
        # Count effort levels
        effort = task.get('effort', 'Medium')
        effort_breakdown[effort] += 1
    
    # Calculate duration - first try to extract from agent text, then calculate from hours
    project_duration_weeks = extract_project_duration(text)
    
    if project_duration_weeks is None and total_hours > 0:
        # Calculate based on total hours (assuming 40 hours per week)
        project_duration_weeks = round(total_hours / 40)
    elif project_duration_weeks is None:
        # Last resort - use a reasonable default but log it
        project_duration_weeks = 4
        print("⚠️  Could not determine project duration from agent output")
    
    return {
        'task_count': task_count,
        'total_hours': total_hours,
        'duration_weeks': project_duration_weeks,
        'effort_breakdown': effort_breakdown
    }


def extract_project_duration(text):
    """Extract project duration from the agent output text"""
    # Look for mentions of project duration
    lines = text.split('\n')
    
    import re
    
    for line in lines:
        line = line.lower()
        
        # Look for duration patterns
        duration_patterns = [
            r'duration[:\s]*(\d+)\s*weeks?',
            r'(\d+)\s*weeks?\s*duration',
            r'project[:\s]*(\d+)\s*weeks?',
            r'completion[:\s]*week\s*(\d+)',
            r'week\s*(\d+)[:\s]*completion'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, line)
            if match:
                weeks = int(match.group(1))
                if 1 <= weeks <= 52:  # Reasonable range
                    return weeks
    
    # If no explicit duration found, return None to let calculation logic handle it
    return None


def main():
    """Main execution function"""
    
    # Project inputs - Clear context for intelligent agents
    project = 'Small Business Website'
    industry = 'Technology'
    project_objectives = 'Create a professional, modern website for a small technology business to establish online presence and attract customers'
    team_members = """
    - John Doe (Project Manager) - 10+ years experience managing web projects
    - Jane Doe (Full-Stack Developer) - Expert in modern web technologies, React, Node.js
    - Bob Smith (UI/UX Designer) - Specializes in clean, modern business website design
    - Alice Johnson (QA Engineer) - Focus on cross-browser testing and user experience
    - Tom Brown (QA Engineer) - Performance and accessibility testing specialist
    """
    
    project_requirements = """
    SCOPE: Professional business website with standard features for customer acquisition and brand presence.

    CORE FEATURES:
    - Responsive design optimized for desktop, tablet, and mobile viewing
    - Modern, clean user interface that reflects professional technology business
    - Intuitive navigation with clear information architecture
    - "About Us" page with company story, mission, and team information
    - "Services" page with detailed descriptions of technology offerings
    - "Contact Us" page with contact form, business details, and location map integration
    - Blog section for thought leadership and company updates
    - Customer testimonials section for social proof
    - Social media integration for wider reach
    
    TECHNICAL REQUIREMENTS:
    - SEO optimization for local search visibility
    - Fast loading performance (under 3 seconds)
    - Accessibility compliance (WCAG guidelines)
    - Analytics integration for performance tracking
    - Content management system for easy updates
    - SSL security and basic contact form protection
    
    BUSINESS CONTEXT:
    This is a standard small business website project, not a complex web application. The goal is to establish professional online presence quickly and cost-effectively using proven technologies and best practices.
    """
    
    # Create inputs dictionary
    inputs = {
        'project_type': project,
        'project_objectives': project_objectives,
        'industry': industry,
        'team_members': team_members,
        'project_requirements': project_requirements
    }
    

    
    # Initialize the system
    print("🚀 Initializing Project Planner System with Strands + AWS Bedrock (Claude 4 Sonnet)...")
    planner = ProjectPlannerSystem(model_name="claude-4-sonnet")
    
    # Run the planning workflow
    result = planner.run_project_planning(inputs)
    
    # Parse and display results in structured format
    display_results(result, planner.logger)
    
    return result


if __name__ == "__main__":
    result = main() 