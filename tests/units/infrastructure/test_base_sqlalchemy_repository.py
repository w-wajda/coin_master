import pytest

from app.infrastructure.repositories.tag_repository import SQLAlchemyTagRepository
from tests.factories import TagFactory


@pytest.fixture
def repository(session_maker):
    return SQLAlchemyTagRepository(session=session_maker)


@pytest.mark.parametrize(
    "method_name, args",
    [
        ("get", (1,)),
        ("get_by", ()),
        ("get_list", ()),
        ("count", ()),
        ("commit", ()),
        ("refresh", (None,)),
        ("all", ()),
        ("delete", (None,)),
    ],
)
async def test_async_methods_without_session_raise(repository, method_name, args):
    method = getattr(repository, method_name)
    with pytest.raises(ValueError):
        await method(*args)


def test_add_without_session_raises(repository):
    with pytest.raises(ValueError):
        repository.add(object())


def test_expire_without_session_raises(repository):
    with pytest.raises(ValueError):
        repository.expire(None)


async def test_use_session_and_get_session(repository, session_maker):
    async with session_maker() as session:
        repository.use_session(session)
        assert repository.get_session() is session


async def test_start_session_commits_on_success(repository, user):
    async with repository.start_session() as session:
        tag = TagFactory(user=user)
        session.add(tag)

    async with repository.start_session():
        found = await repository.get_by(name=tag.name)
    assert found is not None
    assert found.id == tag.id


async def test_start_session_rolls_back_on_exception(repository, user):
    tag_name = "rollback-tag"
    with pytest.raises(RuntimeError):
        async with repository.start_session() as session:
            session.add(TagFactory(name=tag_name, user=user))
            raise RuntimeError("boom")

    async with repository.start_session():
        found = await repository.get_by(name=tag_name)
    assert found is None


async def test_get_returns_by_pk(repository, user):
    async with repository.start_session() as session:
        tag = TagFactory(user=user)
        session.add(tag)

    async with repository.start_session():
        found = await repository.get(tag.id)
    assert found.id == tag.id


async def test_get_by_returns_none_when_missing(repository, user):
    async with repository.start_session():
        missing = await repository.get_by(name="does-not-exist")
    assert missing is None


async def test_get_list_respects_limit_and_offset(repository, user):
    async with repository.start_session() as session:
        for _ in range(3):
            session.add(TagFactory(user=user))

    async with repository.start_session():
        first_page = await repository.get_list(limit=2, offset=0)
        second_page = await repository.get_list(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 1


async def test_count_returns_total_matching_rows(repository, user):
    async with repository.start_session() as session:
        for _ in range(3):
            session.add(TagFactory(user=user))

    async with repository.start_session():
        total = await repository.count(user_id=user.id)

    assert total == 3


async def test_count_ignores_limit_offset_of_get_list(repository, user):
    async with repository.start_session() as session:
        for _ in range(3):
            session.add(TagFactory(user=user))

    async with repository.start_session():
        page = await repository.get_list(limit=1, offset=0, user_id=user.id)
        total = await repository.count(user_id=user.id)

    assert len(page) == 1
    assert total == 3


async def test_all_returns_every_row(repository, user):
    async with repository.start_session() as session:
        session.add(TagFactory(user=user))
        session.add(TagFactory(user=user))

    async with repository.start_session():
        rows = await repository.all()
    assert len(rows) == 2


async def test_refresh_reloads_instance(repository, user):
    async with repository.start_session() as session:
        tag = TagFactory(user=user)
        session.add(tag)

    async with repository.start_session():
        found = await repository.get(tag.id)
        await repository.refresh(found)
    assert found.name == tag.name


async def test_expire_marks_instance_stale(repository, user):
    async with repository.start_session() as session:
        tag = TagFactory(user=user)
        session.add(tag)

    async with repository.start_session():
        found = await repository.get(tag.id)
        repository.expire(found)
        await repository.refresh(found)
        assert found.name == tag.name


async def test_delete_removes_instance(repository, user):
    async with repository.start_session() as session:
        tag = TagFactory(user=user)
        session.add(tag)

    async with repository.start_session():
        found = await repository.get(tag.id)
        await repository.delete(found)
        await repository.commit()

    async with repository.start_session():
        missing = await repository.get(tag.id)
    assert missing is None
