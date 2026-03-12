from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class PublishCrew:
    """Publish Crew for preparing articles for Medium publication"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def seo_optimizer(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_optimizer'],
            verbose=True
        )

    @agent
    def formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['formatter'],
            verbose=True
        )

    @agent
    def linkedin_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['linkedin_creator'],
            verbose=True
        )

    @task
    def optimize_metadata(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_metadata'],
            agent=self.seo_optimizer()
        )

    @task
    def format_for_medium(self) -> Task:
        return Task(
            config=self.tasks_config['format_for_medium'],
            agent=self.formatter(),
            output_file="outputs/article_medium_ready.md"
        )

    @task
    def create_linkedin_content(self) -> Task:
        return Task(
            config=self.tasks_config['create_linkedin_content'],
            agent=self.linkedin_creator(),
            output_file="outputs/linkedin_posts.txt"
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
