import click
import os
from .agent import Agent
from .models import CoachRequest

@click.command(name="hype")
@click.option("--scenario", required=True, help="The scenario you need motivation for")
@click.option("--energy", default=3, type=click.IntRange(1, 3), help="Energy level 1–3 (default: 3)")
def hype(scenario: str, energy: int):
    """Generate a personalized pep talk based on your achievements."""
    if os.path.exists(".env"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass

    request = CoachRequest(
        scenario=scenario,
        energy=energy,
    )

    agent = Agent()
    response = agent.run(request)

    click.echo("\nYour Personalized Pep Talk:")
    click.echo("=" * 50)
    click.echo(response.speech)
    click.echo("=" * 50)

    if response.used_ids:
        click.echo(f"\nBased on achievements: {', '.join(response.used_ids)}")

    click.echo(f"Confidence: {response.confidence:.1%}")

if __name__ == "__main__":
    hype()
