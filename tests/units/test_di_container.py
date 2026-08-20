import pytest
from dependency_injector import providers


def _named_providers(container):
    return [
        (name, p)
        for name, p in container.providers.items()
        if not isinstance(p, (providers.DependenciesContainer, providers.Dependency))
    ]


@pytest.mark.parametrize("kind", ["commands", "queries", "repositories", "services"])
def test_every_provider_can_be_constructed(container, kind):
    """Każdy provider musi dać się zbudować bez TypeError.

    Wyłapuje brakujące zależności w providers.Callable (K1) oraz repozytoria
    nieobecne w kontenerze (K1b) — patrz 02_NAPRAWY_PRZED_MVP.md, krok 3.
    """
    sub = getattr(container, kind)()
    for name, provider in _named_providers(sub):
        try:
            provider()
        except TypeError as exc:
            pytest.fail(f"Provider '{kind}.{name}' nie da się zbudować: {exc}")
