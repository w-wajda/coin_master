import asyncclick as click
from dependency_injector.wiring import (
    Provide,
    inject,
)

from app.domain.users.user_repository import IUserRepository
from app.infrastructure.di import AppContainer


@click.command(name="change_password")
@click.option("--email", prompt="Email", help="User email")
@click.option("--password", prompt="Password", help="New password", hide_input=True, confirmation_prompt=True)
@inject
async def change_password(
    user_repository: IUserRepository = Provide[AppContainer.repositories.user_repository],
    email: str = "",
    password: str = "",
):
    async with user_repository.start_session():
        user = await user_repository.get_by_email(email)
        if not user:
            click.echo(f"User with email {email} does not exists.")
            return

        user.set_password(password)
        await user_repository.commit()

        click.echo(f"Password for user with email {email} has been changed.")
