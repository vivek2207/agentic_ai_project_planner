"""
Workflow Tracker for Sequential Agent Processing
Ensures each agent builds on the previous agent's specific output
"""

import re
from typing import List, Dict, Any

class WorkflowTracker:
    def __init__(self):
        self.task_breakdown = None
        self.estimations = None
        self.allocations = None
        
    def extract_tasks_from_breakdown(self, task_breakdown_text: str) -> List[Dict]:
        """Extract structured task list from planning agent output"""
        tasks = []
        lines = task_breakdown_text.split('\n')
        
        current_task = None
        in_task_list = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Look for task list indicators
            if any(indicator in line.lower() for indicator in ['breakdown:', 'tasks:', 'deliverables:', 'activities:']):
                in_task_list = True
                continue
            
            # Stop if we hit another section
            if line.startswith('Team:') or line.startswith('Timeline:') or line.startswith('Note:'):
                in_task_list = False
                continue
            
            # Only look for tasks when we're in a task list section
            if in_task_list:
                # Much more restrictive task patterns
                task_patterns = [
                    r'^\d+\.\s*(.+?)(?:\s*[\(\:]|$)',  # "1. Task Name"
                    r'^[-•*]\s*(.+?)(?:\s*[\(\:]|$)',   # "- Task Name" or "• Task Name"
                ]
                
                for pattern in task_patterns:
                    match = re.match(pattern, line)
                    if match:
                        if current_task:
                            tasks.append(current_task)
                        
                        task_name = match.group(1).strip()
                        
                        # Skip if too long (likely a section header) or too short
                        if len(task_name) > 100 or len(task_name) < 5:
                            continue
                        
                        # Skip if it looks like a description rather than a task
                        skip_phrases = ['based on', 'this will', 'the team', 'ensure that', 'in order to']
                        if any(phrase in task_name.lower() for phrase in skip_phrases):
                            continue
                            
                        current_task = {
                            'task_name': task_name,
                            'description': '',
                            'estimated_hours': None,
                            'resources': [],
                            'effort_level': 'Medium'
                        }
                        break
                
                # Collect additional details for current task (sub-bullets)
                if current_task and line and not any(re.match(p, line) for p in task_patterns):
                    # Only add if it looks like a sub-task or detail
                    if line.startswith('  ') or line.startswith('\t') or line.startswith('a.') or line.startswith('b.'):
                        if current_task['description']:
                            current_task['description'] += ' ' + line.strip()
                        else:
                            current_task['description'] = line.strip()
        
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)
        
        # Filter out any tasks that are clearly not real tasks
        filtered_tasks = []
        for task in tasks:
            task_name = task['task_name'].lower()
            # Skip if it's clearly not a task
            if not any(action_word in task_name for action_word in [
                'create', 'develop', 'design', 'implement', 'build', 'setup', 'configure', 
                'test', 'deploy', 'write', 'add', 'install', 'optimize', 'integrate'
            ]):
                continue
            filtered_tasks.append(task)
        
        self.task_breakdown = filtered_tasks
        print(f"🔍 Debug: Extracted {len(filtered_tasks)} tasks from agent output")
        return filtered_tasks
    
    def extract_estimates_from_output(self, estimation_text: str) -> List[Dict]:
        """Extract time estimates for the tasks"""
        if not self.task_breakdown:
            return []
        
        # Store raw text for summary extraction
        self._raw_estimation_text = estimation_text
        
        # Update task breakdown with estimates from estimation agent
        lines = estimation_text.split('\n')
        
        for task in self.task_breakdown:
            task_name = task['task_name'].lower()
            task_found = False
            
            # Find estimates for this task in the estimation output
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # More precise matching - look for key words from task name
                task_words = [word for word in task_name.split() if len(word) > 3]  # Skip short words
                if len(task_words) >= 2:
                    # Need at least 2 significant words to match
                    matches = sum(1 for word in task_words if word in line_lower)
                    if matches >= 2:
                        task_found = True
                        # Look in current and next few lines for time estimates
                        search_lines = lines[i:i+3]
                        
                        for search_line in search_lines:
                            # Extract hours - be more specific about hour patterns
                            hour_patterns = [
                                r'(\d+)\s*hours?',
                                r'(\d+)\s*hrs?',
                                r'(\d+)h\b'
                            ]
                            
                            for pattern in hour_patterns:
                                hour_match = re.search(pattern, search_line, re.IGNORECASE)
                                if hour_match:
                                    hours = int(hour_match.group(1))
                                    # Sanity check - reasonable hour range for a task
                                    if 1 <= hours <= 200:
                                        task['estimated_hours'] = hours
                                        break
                            
                            # Extract effort level
                            if 'high effort' in search_line.lower() or 'effort: high' in search_line.lower():
                                task['effort_level'] = 'High'
                            elif 'low effort' in search_line.lower() or 'effort: low' in search_line.lower():
                                task['effort_level'] = 'Low'
                            elif 'medium effort' in search_line.lower() or 'effort: medium' in search_line.lower():
                                task['effort_level'] = 'Medium'
                            
                            # Extract resources
                            resource_keywords = ['designer', 'developer', 'engineer', 'manager', 'qa', 'tester']
                            for keyword in resource_keywords:
                                if keyword in search_line.lower():
                                    if keyword not in [r.lower() for r in task['resources']]:
                                        task['resources'].append(keyword.title())
                        
                        if task_found:
                            break
            
            # If no hours found, set a reasonable default based on task complexity
            if not task['estimated_hours']:
                task_name_lower = task['task_name'].lower()
                if any(word in task_name_lower for word in ['setup', 'planning', 'simple']):
                    task['estimated_hours'] = 8
                elif any(word in task_name_lower for word in ['design', 'develop', 'implement']):
                    task['estimated_hours'] = 16
                elif any(word in task_name_lower for word in ['complex', 'integration', 'testing']):
                    task['estimated_hours'] = 24
                else:
                    task['estimated_hours'] = 12
        
        self.estimations = self.task_breakdown
        return self.task_breakdown
    
    def extract_allocations_from_output(self, allocation_text: str) -> Dict:
        """Extract resource allocations and milestones"""
        if not self.estimations:
            return {'tasks': [], 'milestones': []}
        
        # Store raw text for summary extraction
        self._raw_allocation_text = allocation_text
        
        # Update tasks with specific resource assignments
        lines = allocation_text.split('\n')
        
        team_assignments = {}
        milestones = []
        
        # Extract team member assignments
        team_names = ['john doe', 'jane doe', 'bob smith', 'alice johnson', 'tom brown']
        
        for line in lines:
            line_lower = line.lower()
            
            # Look for milestone patterns
            milestone_patterns = [
                r'milestone[:\s]*(.+)',
                r'phase[:\s]*(.+)',
                r'deliverable[:\s]*(.+)'
            ]
            
            for pattern in milestone_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    milestone_name = match.group(1).strip()
                    if len(milestone_name) < 100:  # Reasonable length
                        milestones.append({
                            'milestone_name': milestone_name.title(),
                            'tasks': [],  # Will be populated based on task assignments
                            'timeline': self._extract_timeline_from_context(lines, line)
                        })
            
            # Look for team assignments
            for name in team_names:
                if name in line_lower:
                    # Find what tasks are mentioned near this team member
                    for task in self.estimations:
                        task_words = task['task_name'].lower().split()[:3]
                        if any(word in line_lower for word in task_words):
                            if 'assigned_to' not in task:
                                task['assigned_to'] = []
                            if name.title() not in task['assigned_to']:
                                task['assigned_to'].append(name.title())
        
        # Group tasks into milestones based on similarity and dependencies
        if milestones:
            self._assign_tasks_to_milestones(milestones)
        
        result = {
            'tasks': self.estimations,
            'milestones': milestones
        }
        
        self.allocations = result
        return result
    
    def _extract_timeline_from_context(self, lines: List[str], current_line: str) -> str:
        """Extract timeline information from context"""
        current_index = lines.index(current_line) if current_line in lines else 0
        
        # Look in nearby lines for week/day mentions
        search_range = lines[max(0, current_index-2):current_index+3]
        
        for line in search_range:
            week_match = re.search(r'week\s*(\d+)', line.lower())
            if week_match:
                return f"Week {week_match.group(1)}"
            
            day_match = re.search(r'(\d+)\s*days?', line.lower())
            if day_match:
                return f"{day_match.group(1)} days"
        
        return "TBD"
    
    def _assign_tasks_to_milestones(self, milestones: List[Dict]):
        """Assign tasks to appropriate milestones based on task type"""
        if not self.estimations or not milestones:
            return
        
        # Simple assignment based on task names
        for task in self.estimations:
            task_name = task['task_name'].lower()
            
            # Assign to most relevant milestone
            best_milestone = None
            best_score = 0
            
            for milestone in milestones:
                milestone_name = milestone['milestone_name'].lower()
                
                # Calculate relevance score
                score = 0
                task_words = set(task_name.split())
                milestone_words = set(milestone_name.split())
                
                # Common words between task and milestone
                common_words = task_words.intersection(milestone_words)
                score += len(common_words) * 2
                
                # Keyword matching
                if any(word in task_name for word in ['design', 'wireframe', 'mockup']) and \
                   any(word in milestone_name for word in ['design', 'planning', 'setup']):
                    score += 3
                elif any(word in task_name for word in ['develop', 'code', 'implement']) and \
                     any(word in milestone_name for word in ['develop', 'implementation', 'build']):
                    score += 3
                elif any(word in task_name for word in ['test', 'qa', 'review']) and \
                     any(word in milestone_name for word in ['test', 'quality', 'review']):
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_milestone = milestone
            
            # Assign task to best matching milestone
            if best_milestone:
                best_milestone['tasks'].append(task['task_name'])
    
    def get_unified_summary(self) -> Dict:
        """Get unified summary by extracting agent's actual calculations"""
        if not self.allocations:
            return {}
        
        # Get raw agent outputs to extract their actual numbers
        raw_estimation = getattr(self, '_raw_estimation_text', '')
        raw_allocation = getattr(self, '_raw_allocation_text', '')
        
        # Extract agent's actual summary numbers
        actual_summary = self._extract_agent_summary(raw_estimation, raw_allocation)
        
        # Use the actual task count and hours from agents, not our parsing
        tasks = self.allocations['tasks']
        milestones = self.allocations['milestones']
        
        # If we found agent's actual numbers, use those; otherwise fallback to parsing
        if actual_summary['total_hours'] > 0:
            total_hours = actual_summary['total_hours']
            total_tasks = actual_summary['total_tasks']
            total_weeks = actual_summary['total_weeks']
        else:
            # Fallback: use parsing but with sanity checks
            valid_tasks = [task for task in tasks if task.get('estimated_hours', 0) > 0]
            total_hours = sum(task.get('estimated_hours', 0) for task in valid_tasks)
            total_tasks = len(valid_tasks)
            total_weeks = max(1, round(total_hours / 40)) if total_hours > 0 else 4
        
        # Effort breakdown from actual tasks
        effort_breakdown = {'High': 0, 'Medium': 0, 'Low': 0}
        for task in tasks:
            effort = task.get('effort_level', 'Medium')
            effort_breakdown[effort] += 1
        
        print(f"🔍 Agent Summary Extraction:")
        print(f"   • Agent estimated hours: {total_hours}")
        print(f"   • Agent estimated tasks: {total_tasks}")
        print(f"   • Agent estimated weeks: {total_weeks}")
        print(f"   • Math check: {total_hours}h ÷ 5 people = {total_hours/5:.1f}h per person")
        
        return {
            'total_tasks': total_tasks,
            'total_hours': total_hours,
            'total_weeks': total_weeks,
            'effort_breakdown': effort_breakdown,
            'tasks_with_details': tasks[:total_tasks],  # Limit to actual count
            'milestones': milestones
        }
    
    def _extract_agent_summary(self, estimation_text: str, allocation_text: str) -> Dict:
        """Extract the agent's actual calculated summary"""
        import re
        
        combined_text = estimation_text + "\n" + allocation_text
        
        # Look for agent's summary numbers
        total_hours = 0
        total_tasks = 0
        total_weeks = 0
        
        # Extract total hours from agent output
        hour_patterns = [
            r'Total Estimated Hours[:\s]*(\d+)\s*hours?',
            r'Total[:\s]*(\d+)\s*hours?',
            r'(\d+)\s*hours?\s*total',
            r'Project\s*total[:\s]*(\d+)\s*hours?'
        ]
        
        for pattern in hour_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                hours = int(match.group(1))
                if 50 <= hours <= 2000:  # Reasonable range
                    total_hours = hours
                    break
        
        # Extract total duration from agent output
        duration_patterns = [
            r'Total Estimated Duration[:\s]*(\d+)\s*weeks?',
            r'Duration[:\s]*(\d+)\s*weeks?',
            r'(\d+)\s*weeks?\s*total',
            r'(\d+)\s*weeks?\s*duration'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                weeks = int(match.group(1))
                if 1 <= weeks <= 52:  # Reasonable range
                    total_weeks = weeks
                    break
        
        # Extract task count - count actual numbered tasks in breakdown
        task_count_patterns = [
            r'## \*\*PHASE \d+:',  # Count phases (escape asterisks)
            r'### \*\*Task \d+\.\d+:',  # Count sub-tasks (escape asterisks)
            r'^\d+\.\d+:',  # Count numbered tasks
            r'Task \d+\.\d+:',  # Alternative task pattern
        ]
        
        for pattern in task_count_patterns:
            try:
                matches = re.findall(pattern, combined_text, re.MULTILINE | re.IGNORECASE)
                if matches:
                    total_tasks = len(matches)
                    break
            except re.error:
                continue  # Skip invalid patterns
        
        # If no task count found, estimate from hours (average 15-20 hours per task)
        if total_tasks == 0 and total_hours > 0:
            total_tasks = max(5, min(25, round(total_hours / 18)))
        
        return {
            'total_hours': total_hours,
            'total_tasks': total_tasks,  
            'total_weeks': total_weeks
        } 