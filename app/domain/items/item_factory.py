import factory

from app.domain.items.item import Item
from app.domain.users.user_factory import (
    UserDictFactory,
    UserFactory,
)


class ItemFactory(factory.Factory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    price = factory.Sequence(lambda n: "%.2f" % (n + 1 + 0.99))
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Item


class ItemDictFactory(factory.DictFactory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    price = factory.Sequence(lambda n: "%.2f" % (n + 1 + 0.99))
    user = factory.SubFactory(UserDictFactory)
