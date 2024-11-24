import factory

from app.domain.tags.tag import Tag
from app.domain.users.user_factory import (
    UserDictFactory,
    UserFactory,
)


class TagFactory(factory.Factory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Tag


class TagDictFactory(factory.DictFactory):
    name = factory.SubFactory(lambda n: "Name %03d" % n)
    user = factory.SubFactory(UserDictFactory)
