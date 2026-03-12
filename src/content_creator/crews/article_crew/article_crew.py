from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from content_creator.tools import search_topic_info


@CrewBase
class ArticleCrew:
    """Article Crew for creating Medium-style educational articles"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def research_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['research_specialist'],
            tools=[search_topic_info],
            verbose=True
        )

    @agent
    def content_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['content_planner'],
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True
        )

    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config['editor'],
            verbose=True
        )

    @agent
    def code_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['code_specialist'],
            verbose=True
        )

    @task
    def deep_research(self) -> Task:
        return Task(
            config=self.tasks_config['deep_research'],
            agent=self.research_specialist()
        )

    @task
    def create_outline(self) -> Task:
        return Task(
            config=self.tasks_config['create_outline'],
            agent=self.content_planner()
        )

    @task
    def write_article(self) -> Task:
        return Task(
            config=self.tasks_config['write_article'],
            agent=self.writer()
        )

    @task
    def edit_article(self) -> Task:
        return Task(
            config=self.tasks_config['edit_article'],
            agent=self.editor(),
            output_file="articles/draft_{topic_title}.md"
        )

    @task
    def create_project(self) -> Task:
        return Task(
            config=self.tasks_config['create_project'],
            agent=self.code_specialist(),
            output_file="articles/project_{topic_title}.md"
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )