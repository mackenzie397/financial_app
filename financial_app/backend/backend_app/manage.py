import click
from flask.cli import with_appcontext
from financial_app.backend.backend_app.wsgi import app
from src.main import seed_initial_data

@click.group()
def cli():
    pass

from src.models.user import User, db
from src.models.category import Category
from src.models.payment_method import PaymentMethod

@click.command(name='backfill_defaults')
@with_appcontext
def backfill_defaults_command():
    """
    Backfills default categories and payment methods for users who don't have them.
    """
    users = User.query.all()
    total_users = len(users)
    updated_count = 0

    click.echo(f"Found {total_users} users to check.")

    for user in users:
        # Check if the user already has categories
        if Category.query.filter_by(user_id=user.id).count() == 0:
            updated_count += 1
            click.echo(f"Updating user {user.username} (ID: {user.id}) with default items.")

            # Create default expense categories
            default_expense_categories = [
                "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde",
                "Educação", "Investimentos", "Outros"
            ]
            for name in default_expense_categories:
                db.session.add(Category(name=name, user_id=user.id, category_type='expense'))

            # Create default income categories
            default_income_categories = [
                "Salário", "Renda Extra", "Investimentos", "Outros"
            ]
            for name in default_income_categories:
                db.session.add(Category(name=name, user_id=user.id, category_type='income'))

            # Create default payment methods
            default_payment_methods = [
                "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX",
                "Transferência Bancária"
            ]
            for name in default_payment_methods:
                db.session.add(PaymentMethod(name=name, user_id=user.id))
        else:
            click.echo(f"User {user.username} (ID: {user.id}) already has categories. Skipping.")

    if updated_count > 0:
        db.session.commit()
        click.echo(f"Successfully updated {updated_count} users.")
    else:
        click.echo("No users needed updating.")

@click.command(name='seed_db')
@with_appcontext
def seed_db_command():
    """Seeds the database with initial data."""
    seed_initial_data(app)

cli.add_command(backfill_defaults_command)
cli.add_command(seed_db_command)

if __name__ == '__main__':
    cli()
