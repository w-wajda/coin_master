from app.domain.tokens.token_repository import ITokenRepository


class RevokeTokenCommand:
    def __init__(self, token_repository: ITokenRepository):
        self.token_repository = token_repository

    async def __call__(self, token_str: str) -> None:
        async with self.token_repository.start_session():
            if token := await self.token_repository.get_by(token=token_str):
                token.is_active = False
                await self.token_repository.commit()
