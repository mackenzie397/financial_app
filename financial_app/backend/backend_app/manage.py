import click
from flask.cli import with_appcontext
from financial_app.backend.backend_app.wsgi import app
from src.main import seed_initial_data

@click.group()
def cli():
    pass

@click.command(name='seed_db')
@with_appcontext
def seed_db_command():
    """Seeds the database with initial data."""
    seed_initial_data(app)

cli.add_command(seed_db_command)

if __name__ == '__main__':
    cli()
