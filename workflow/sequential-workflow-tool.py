"""Example of a sequential workflow using three agents as a workflow tool (strands-agents-tools)"""

import boto3
from strands import Agent
from strands.models import BedrockModel
from strands_tools import workflow
import os
os.environ["AWS_REGION"] = "us-east-1"

# Configure AWS region for Bedrock
AWS_REGION = "us-east-1"  # Claude 3.7 Sonnet is available in us-east-1
CLAUDE_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"




BLOG_PLANNER_INSTRUCTION = "You are a blog planner. Take the topic that is provided to you and create a detailed outline with 3 sections and key points for each section."
SECTION_WRITER_INSTRUCTION = "You are a blog writer. Take the outline provided by the blog planner and expand each section into a detailed paragraph."
EDITOR_INSTRUCTION = "You are a professional editor. Improve the following blog draft by fixing grammar, making sentences concise, and ensuring smooth flow."

if __name__ == "__main__":

    # Verify AWS credentials are configured
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            print("⚠️  AWS credentials not found. Please configure your AWS credentials.")
            print("   You can use: aws configure")
            print("   Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        else:
            print("✓ AWS credentials configured")
            
        # Test Bedrock access
        bedrock = boto3.client('bedrock', region_name=AWS_REGION)
        print("✓ Amazon Bedrock client initialized")
        
    except Exception as e:
        print(f"✗ Error setting up AWS: {e}")
        print("Please ensure you have proper AWS credentials and permissions for Bedrock.")
        exit(1)


    # Verification test
    print("🔍 Testing installation...")

    try:
        from strands import Agent
        from strands_tools import calculator, swarm, agent_graph, workflow
        print("✅ All required imports successful!")
        
        # Test basic agent creation (without calling the model)
        test_agent = Agent(
            model=CLAUDE_MODEL_ID,
            system_prompt="You are a test agent.",
            tools=[workflow]
        )
        print("✅ Claude 3.7 Sonnet agent creation successful!")
        print("\n🎉 Installation verified - ready to proceed with multi-agent systems!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Try running one of the alternative installation methods above.")
    except Exception as e:
        print(f"⚠️  Agent creation issue: {e}")
        print("   This might be an AWS credentials issue - we'll address this in the next section.")
        
    # Define the model we use for the agents (we want creative response that's why temp is high)
    #bedrock_model = BedrockModel(
    #    model_id=CLAUDE_MODEL_ID, #"us.amazon.nova-premier-v1:0",
    #    temperature=0.9,
    #    region_name=AWS_REGION,
    #)

    # Create one Agent with one workflow tool
    blog_agent = Agent( model=CLAUDE_MODEL_ID, tools=[workflow])

    # Creating the workflow
    blog_agent.tool.workflow(
        action="create",
        workflow_id="blog_agent_workflow",
        tasks=[
            {
                "model_provider": "bedrock",  
                "model_settings":{"model_id":CLAUDE_MODEL_ID},
                "task_id": "blog_planner",  # The unique ID for the Blog Planner agent
                "description": 'Create a detailed outline for the blog post about "The Future of AI in Content Creation"',  # The description of the task
                "system_prompt": BLOG_PLANNER_INSTRUCTION,  # The system prompt for the Blog Planner agent
                "priority": 5,  # The priority of the task (higher numbers indicate higher priority)
            },
            {
                "model_provider": "bedrock",  
                "model_settings":{"model_id":CLAUDE_MODEL_ID},
                "task_id": "section_writer",
                "description": "Expand each section of the outline into a detailed paragraph",
                "dependencies": ["blog_planner"],
                "system_prompt": SECTION_WRITER_INSTRUCTION,
                "priority": 4,
            },
            {
                "model_provider": "bedrock",  
                "model_settings":{"model_id":CLAUDE_MODEL_ID},
                "task_id": "editor",
                "description": "Edit the blog draft for clarity and conciseness",
                "dependencies": ["section_writer"],
                "system_prompt": EDITOR_INSTRUCTION,
                "priority": 3,
            },
        ],
    )

    # Start the workflow
    blog_agent.tool.workflow(
        action="start",
        workflow_id="blog_agent_workflow",
    )

    # Monitor the workflow progress
    blog_agent.tool.workflow(
        action="monitor",
        workflow_id="blog_agent_workflow",
    )
