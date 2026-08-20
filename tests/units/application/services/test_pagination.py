from app.application.services.pagination import PaginationService


def test_get_items_sets_total_and_computes_pages():
    service = PaginationService(page=1, limit=10)

    result = service.get_items(items=[1, 2, 3], total=25)

    assert result.total == 25
    assert result.pages == 3


def test_get_items_pages_rounds_up_partial_page():
    service = PaginationService(page=1, limit=10)

    result = service.get_items(items=[], total=21)

    assert result.pages == 3


def test_get_items_pages_is_zero_for_no_results():
    service = PaginationService(page=1, limit=10)

    result = service.get_items(items=[], total=0)

    assert result.pages == 0


def test_offset_computed_from_page_and_limit():
    service = PaginationService(page=3, limit=20)

    assert service.offset == 40
