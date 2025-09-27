import click
import os
from .agent import Agent
from .models import CoachRequest


@click.command()
@click.option('--scenario', required=True, help='The scenario you need motivation for')
@click.option('--energy', default=2, type=int, help='Energy level 1-5 (default: 2)')
@click.option('--persona', default='coach', help='Coach persona (default: coach)')
def hype(scenario, energy, persona):
    """Generate a personalized pep talk based on your achievements."""
    
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    request = CoachRequest(
        scenario=scenario,
        energy=energy,
        persona=persona
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


if __name__ == '__main__':
    hype()
