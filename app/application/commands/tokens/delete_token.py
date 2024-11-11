from app.domain.tokens.token_repository import ITokenRepository


class DeleteTokenCommand:
    def __init__(self, token_repository: ITokenRepository):
        self.token_repository = token_repository

    async def __call__(self, user_id: int, uuid: str) -> None:
        async with self.token_repository.start_session():
            if token := await self.token_repository.get_by(uuid=uuid, user_id=user_id):
                token.is_active = False
                await self.token_repository.commit()
