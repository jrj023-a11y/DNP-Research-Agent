import os
from crewai import Agent, Task, Crew, Process

# 1. Define your Agents
researcher = Agent(
  role='Cardiovascular Research Specialist',
  goal='Find the latest clinical trials on asymptomatic aortic stenosis and TAVR',
  backstory="""You are an expert medical researcher at an academic hospital. 
  You excel at finding peer-reviewed studies and clinical trial data.""",
  verbose=True,
  allow_delegation=False
)

analyst = Agent(
  role='DNP Clinical Analyst',
  goal='Summarize findings with a focus on KCCQ scores and patient outcomes',
  backstory="""You are a Doctor of Nursing Practice student specializing in 
  cardiac surgery. You turn complex data into actionable clinical summaries.""",
  verbose=True
)

# 2. Define the Tasks
task1 = Task(description="Search for 2025-2026 trials on asymptomatic AS.", agent=researcher)
task2 = Task(description="Summarize the impact of early intervention on KCCQ-12 scores.", agent=analyst)

# 3. Form the Crew
crew = Crew(
  agents=[researcher, analyst],
  tasks=[task1, task2],
  process=Process.sequential
)

result = crew.kickoff()
print(result)
