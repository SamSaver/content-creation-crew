from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from content_creator.tools import (
    search_arxiv,
    search_ai_news,
    search_github_trending,
    get_trending_ai_topics,
    save_topic
)


@CrewBase
class ResearchCrew:
    """Research Crew for discovering and curating AI/ML topics"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def trend_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['trend_scout'],
            tools=[
                search_arxiv,
                search_ai_news,
                search_github_trending,
                get_trending_ai_topics
            ],
            verbose=True
        )

    @agent
    def impact_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['impact_analyst'],
            verbose=True
        )

    @agent
    def topic_curator(self) -> Agent:
        return Agent(
            config=self.agents_config['topic_curator'],
            tools=[save_topic],
            verbose=True
        )

    @task
    def discover_topics(self) -> Task:
        return Task(
            config=self.tasks_config['discover_topics'],
            agent=self.trend_scout()
        )

    @task
    def analyze_impact(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_impact'],
            agent=self.impact_analyst()
        )

    @task
    def curate_findings(self) -> Task:
        return Task(
            config=self.tasks_config['curate_findings'],
            agent=self.topic_curator()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )