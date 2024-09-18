import sys
import datetime
from crewai import Crew, Process, Task, Agent
from browserbase import browserbase
from kayak import kayak
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


flights_agent = Agent(
    role="Flights",
    goal="Search flights",
    backstory="An agent that can search for flights.",
    tools=[kayak, browserbase],
    allow_delegation=False,
)

summarize_agent = Agent(
    role="Summarize",
    goal="Summarize content",
    backstory="An agent that can summarize text.",
    allow_delegation=False,
)

output_search_example = """
Here are our top 5 flights from Sofia to Berlin on 24th May 2024:
1. Bulgaria Air: Departure: 14:45, Arrival: 15:55, Duration: 2 hours 10 minutes, Layovers: Munich, 2 hours layover, Price: $123, Details: https://www.kayak.com/some-url-to-book
"""

search_task = Task(
    description=(
        "Search flights according to criteria {request}. Current year: {current_year}"
    ),
    expected_output=output_search_example,
    agent=flights_agent,
    output_file="flights_search.txt",
)

output_providers_example = """
Here are our top 5 picks from Sofia to Berlin on 24th May 2024:
1. Bulgaria Air:
   - Departure: 14:45
   - Arrival: 15:55
   - Duration: 2 hours 10 minutes
   - Layovers: Munich, 2 hours layover
   - Price: $123
   - Booking: [MyTrip](https://www.kayak.com/some-url-to-book)
"""

search_booking_providers_task = Task(
    description="Load every flight individually and find available booking providers",
    expected_output=output_providers_example,
    agent=flights_agent,
    output_file="flights_providers.txt",
)

crew = Crew(
    agents=[flights_agent, summarize_agent],
    tasks=[search_task, search_booking_providers_task],
    # let's cap the number of OpenAI requests as the Agents
    #   may have to do multiple costly calls with large context
    max_rpm=100,
    verbose=True,
    planning=True,
)

result = crew.kickoff(
    inputs={
        "request": sys.argv[1],
        "current_year": datetime.date.today().year,
    }
)

print("Got result", result)
