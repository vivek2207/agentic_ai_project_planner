import os
from datetime import datetime
import json

class OutputFormatter:
    def __init__(self, project_name="Website Project"):
        self.project_name = project_name
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create outputs directory
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
    
    def save_html_report(self, tasks_data, milestones_data, result_text, summary_data):
        """Save project planning results as HTML file"""
        
        filename = f"outputs/project_plan_{self.timestamp}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.project_name} - Planning Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .summary-box {{ background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-weight: bold; color: #2980b9; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
        .effort-high {{ background-color: #e74c3c; color: white; }}
        .effort-medium {{ background-color: #f39c12; color: white; }}
        .effort-low {{ background-color: #27ae60; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 {self.project_name} - Planning Report</h1>
        <p class="timestamp">Generated on: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
        
        <div class="summary-box">
            <h2>📈 Project Summary</h2>
            {self._generate_summary_html(summary_data)}
        </div>
        
        <h2>📊 Task Breakdown & Estimates</h2>
        {self._generate_tasks_html(tasks_data)}
        
        <h2>🎯 Project Milestones</h2>
        {self._generate_milestones_html(milestones_data)}
        
        <h2>👥 Team Allocation</h2>
        {self._generate_team_html()}
        
        <h2>📄 Detailed Agent Output</h2>
        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; white-space: pre-line; font-family: monospace; font-size: 0.9em;">
{result_text}
        </div>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def save_markdown_report(self, tasks_data, milestones_data, result_text, summary_data):
        """Save project planning results as Markdown file"""
        
        filename = f"outputs/project_plan_{self.timestamp}.md"
        
        md_content = f"""# 📋 {self.project_name} - Planning Report

*Generated on: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}*

## 📈 Project Summary

{self._generate_summary_markdown(summary_data)}

## 📊 Task Breakdown & Estimates

{self._generate_tasks_markdown(tasks_data)}

## 🎯 Project Milestones

{self._generate_milestones_markdown(milestones_data)}

## 👥 Team Allocation

{self._generate_team_markdown()}

## 📄 Detailed Agent Output

```
{result_text}
```

---
*Report generated by Strands Project Planner*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filename
    
    def _generate_summary_html(self, summary_data):
        """Generate HTML for project summary"""
        if not summary_data:
            return "<p>Summary data not available</p>"
        
        return f"""
        <div class="metric">📊 <strong>Total Tasks:</strong> <span class="metric-value">{summary_data.get('task_count', 'N/A')}</span></div>
        <div class="metric">⏱️ <strong>Total Effort:</strong> <span class="metric-value">{summary_data.get('total_hours', 'N/A')} hours</span></div>
        <div class="metric">📅 <strong>Duration:</strong> <span class="metric-value">{summary_data.get('duration_weeks', 'N/A')} weeks</span></div>
        <div class="metric">👥 <strong>Team Size:</strong> <span class="metric-value">5 members</span></div>
        """
    
    def _generate_summary_markdown(self, summary_data):
        """Generate Markdown for project summary"""
        if not summary_data:
            return "Summary data not available"
        
        return f"""
| Metric | Value |
|--------|-------|
| 📊 Total Tasks | {summary_data.get('task_count', 'N/A')} |
| ⏱️ Total Effort | {summary_data.get('total_hours', 'N/A')} hours |
| 📅 Duration | {summary_data.get('duration_weeks', 'N/A')} weeks |
| 👥 Team Size | 5 members |
"""
    
    def _generate_tasks_html(self, tasks_data):
        """Generate HTML table for tasks"""
        if not tasks_data:
            return "<p>No tasks found</p>"
        
        rows = ""
        for task in tasks_data:
            effort_class = f"effort-{task.get('effort', 'medium').lower()}"
            resources = ", ".join(task.get('resources', ['TBD']))
            
            rows += f"""
            <tr>
                <td>{task.get('task_name', 'N/A')}</td>
                <td>{task.get('estimated_time', 'N/A')}</td>
                <td><span class="{effort_class}">{task.get('effort', 'Medium')}</span></td>
                <td>{resources}</td>
            </tr>
            """
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Task Name</th>
                    <th>Estimated Time</th>
                    <th>Effort Level</th>
                    <th>Resources</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_tasks_markdown(self, tasks_data):
        """Generate Markdown table for tasks"""
        if not tasks_data:
            return "No tasks found"
        
        md = "| Task Name | Estimated Time | Effort Level | Resources |\n"
        md += "|-----------|----------------|--------------|-----------|\\n"
        
        for task in tasks_data:
            resources = ", ".join(task.get('resources', ['TBD']))
            md += f"| {task.get('task_name', 'N/A')} | {task.get('estimated_time', 'N/A')} | {task.get('effort', 'Medium')} | {resources} |\n"
        
        return md
    
    def _generate_milestones_html(self, milestones_data):
        """Generate HTML table for milestones"""
        if not milestones_data:
            return "<p>No milestones found</p>"
        
        rows = ""
        for milestone in milestones_data:
            rows += f"""
            <tr>
                <td>{milestone.get('milestone_name', 'N/A')}</td>
                <td>{milestone.get('timeline', 'N/A')}</td>
                <td>{milestone.get('status', 'Pending')}</td>
            </tr>
            """
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Milestone</th>
                    <th>Timeline</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_milestones_markdown(self, milestones_data):
        """Generate Markdown table for milestones"""
        if not milestones_data:
            return "No milestones found"
        
        md = "| Milestone | Timeline | Status |\n"
        md += "|-----------|----------|--------|\n"
        
        for milestone in milestones_data:
            md += f"| {milestone.get('milestone_name', 'N/A')} | {milestone.get('timeline', 'N/A')} | {milestone.get('status', 'Pending')} |\n"
        
        return md
    
    def _generate_team_html(self):
        """Generate HTML for team allocation"""
        team_members = {
            'John Doe': {'role': 'Project Manager', 'tasks': 'Planning, Coordination, Risk Management'},
            'Jane Doe': {'role': 'Software Engineer', 'tasks': 'Development, Performance, SEO'},
            'Bob Smith': {'role': 'Designer', 'tasks': 'UI/UX, Responsive Design, Mockups'},
            'Alice Johnson': {'role': 'QA Engineer', 'tasks': 'Testing, Quality Assurance'},
            'Tom Brown': {'role': 'QA Engineer', 'tasks': 'Testing, Quality Assurance'}
        }
        
        rows = ""
        for name, info in team_members.items():
            rows += f"""
            <tr>
                <td>{name}</td>
                <td>{info['role']}</td>
                <td>{info['tasks']}</td>
            </tr>
            """
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Team Member</th>
                    <th>Role</th>
                    <th>Primary Tasks</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_team_markdown(self):
        """Generate Markdown for team allocation"""
        team_members = {
            'John Doe': {'role': 'Project Manager', 'tasks': 'Planning, Coordination, Risk Management'},
            'Jane Doe': {'role': 'Software Engineer', 'tasks': 'Development, Performance, SEO'},
            'Bob Smith': {'role': 'Designer', 'tasks': 'UI/UX, Responsive Design, Mockups'},
            'Alice Johnson': {'role': 'QA Engineer', 'tasks': 'Testing, Quality Assurance'},
            'Tom Brown': {'role': 'QA Engineer', 'tasks': 'Testing, Quality Assurance'}
        }
        
        md = "| Team Member | Role | Primary Tasks |\n"
        md += "|-------------|------|---------------|\n"
        
        for name, info in team_members.items():
            md += f"| {name} | {info['role']} | {info['tasks']} |\n"
        
        return md 