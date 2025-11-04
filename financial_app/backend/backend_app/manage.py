import click
from flask.cli import with_appcontext
from src.main import create_app, seed_initial_data
from src.models.user import db
import os

# Create a dummy app to get the context
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@click.group()
def cli():
    pass

@click.command(name='create_db')
@with_appcontext
def create_db_command():
    """Creates the database tables."""
    db.create_all()
    print('Database created!')

@click.command(name='seed_db')
@with_appcontext
def seed_db_command():
    """Seeds the database with initial data."""
    seed_initial_data(app)
    print('Database seeded!')

cli.add_command(create_db_command)
cli.add_command(seed_db_command)

if __name__ == '__main__':
    cli()
