"""
Simple structure test for Strands Project Planner
Tests imports and basic configuration loading without running AWS calls
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models import ProjectPlan, TaskEstimate, Milestone
        print("✅ Models imported successfully")
        
        # Test Pydantic models
        sample_task = TaskEstimate(
            task_name="Test Task",
            estimated_time_hours=10.0,
            required_resources=["Developer"]
        )
        print("✅ Pydantic models working")
        
        import yaml
        print("✅ YAML module available")
        
        import pandas as pd
        print("✅ Pandas available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_config_loading():
    """Test YAML config loading"""
    try:
        import yaml
        
        # Test agents config
        with open('config/agents.yaml', 'r') as file:
            agents_config = yaml.safe_load(file)
        print("✅ Agents config loaded")
        print(f"   Found {len(agents_config)} agents: {list(agents_config.keys())}")
        
        # Test tasks config  
        with open('config/tasks.yaml', 'r') as file:
            tasks_config = yaml.safe_load(file)
        print("✅ Tasks config loaded")
        print(f"   Found {len(tasks_config)} tasks: {list(tasks_config.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_aws_config():
    """Test AWS configuration (without actual AWS calls)"""
    try:
        # Test import without calling AWS
        import boto3
        print("✅ Boto3 available")
        
        # Note: We won't actually test Bedrock connection here
        # That requires valid AWS credentials
        
        return True
        
    except ImportError:
        print("❌ Boto3 not installed - run: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ AWS config error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Strands Project Planner Structure")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Config Loading", test_config_loading), 
        ("AWS Dependencies", test_aws_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔧 {test_name}:")
        results.append(test_func())
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All structure tests passed!")
        print("📋 Ready to configure AWS credentials and run main.py")
    else:
        print("⚠️  Some tests failed - check dependencies")
    
    print("\n📁 Project Structure:")
    print("strands-project-planner/")
    print("├── main.py              # Main execution script")
    print("├── models.py            # Pydantic data models")
    print("├── aws_config.py        # AWS Bedrock configuration")
    print("├── requirements.txt     # Dependencies")
    print("├── README.md            # Setup instructions")
    print("├── .env.template        # Environment template")
    print("└── config/")
    print("    ├── agents.yaml      # Agent configurations")
    print("    └── tasks.yaml       # Task definitions")

if __name__ == "__main__":
    main() 