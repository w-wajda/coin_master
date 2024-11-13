import asyncclick as click
from dependency_injector.wiring import (
    Provide,
    inject,
)

from app.domain.users.user import User
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.di import AppContainer


@click.command(name="create_superuser")
@click.option("--email", prompt="Email", help="Email for the superuser")
@click.option(
    "--password", prompt="Password", help="Password for the superuser", hide_input=True, confirmation_prompt=True
)
@inject
async def create_superuser(
    user_repository: IUserRepository = Provide[AppContainer.repositories.user_repository],
    email: str = "",
    password: str = "",
):
    """
    Create a superuser command for the CLI
    Creates a superuser in the database with the provided email and password
    """
    async with user_repository.start_session():
        existing_user = await user_repository.get_by_email(email)
        if existing_user:
            click.echo(f"User with email {email} already exists.")
            return

        user = User(email=email)
        user.set_password(password)
        user.is_staff = True

        user_repository.add(user)
        await user_repository.commit()

        click.echo(f"Superuser with email {email} has been created.")
