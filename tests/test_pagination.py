from rfcommon_api.common.paginators import Pagination, PaginationException
from unittest import TestCase


class TestPaging(TestCase):

    def test_valid_form(self):
        pager = Pagination(1, "/test_ur")

        pager.set_paging_info({})
        self.assertEqual(pager.page, 1)
        self.assertEqual(pager.per_page, 1)

    def test_valid_page(self):
        items_count = 10000
        pager = Pagination(items_count, "/test_ur", page=10, per_page=100)
        self.assertEqual(pager.pages, 100)
        self.assertEqual(pager.page, 10)
        self.assertEqual(pager.has_prev, True)
        self.assertEqual(pager.has_next, True)
        self.assertEqual(pager.first_item, 900)
        self.assertEqual(pager.last_item, 1000)
        self.assertEqual(pager.is_valid_page, True)

    def test_invalid_page(self):
        items_count = 10000
        with self.assertRaises(PaginationException):
            Pagination(items_count, "/test_ur", page=0, per_page=0)
        pager = Pagination(items_count, "/test_ur")
        with self.assertRaises(PaginationException) as pe:
            pager.set_paging_info({"page": -1})
        self.assertDictEqual(pe.exception.args[0], {"page": ["Not a valid positive value."]})
        with self.assertRaises(PaginationException) as pe:
            pager.set_paging_info({"per_page": -10})
        self.assertDictEqual(pe.exception.args[0], {"per_page": ["Not a valid positive value."]})
        self.assertEqual(pager.pages, 1)
        self.assertEqual(pager.has_prev, False)
        self.assertEqual(pager.has_next, False)
        self.assertEqual(pager.first_item, 0)
        self.assertEqual(pager.last_item, items_count)
        self.assertEqual(pager.is_valid_page, True)
        self.assertDictEqual(
            pager.pagination_headers(),
            {
                "Link": '</test_ur?per_page=10000&page=1>; rel="first"',
                "X-Pagination-Current-Page": 1,
                "X-Pagination-Per-Page": 10000,
                "X-Pagination-Total-Count": 10000,
            },
        )
        pager.page = 0
        self.assertEqual(pager.pages, 1)

    def test_not_single_page(self):
        items_count = 10000
        pager = Pagination(items_count, "/test_ur")
        pager.set_paging_info({"page": 5, "per_page": 300})
        self.assertEqual(pager.pages, 34)
        self.assertEqual(pager.has_prev, True)
        self.assertEqual(pager.has_next, True)
        self.assertEqual(pager.first_item, 1200)
        self.assertEqual(pager.last_item, 1500)
        self.assertEqual(pager.is_valid_page, True)
        link = (
            "</test_ur?per_page=300&page=1>; "
            + 'rel="first", </test_ur?per_page=300&page=6>; '
            + 'rel="next", </test_ur?per_page=300&page=4>; '
            + 'rel="prev", </test_ur?per_page=300&page=34>; '
            + 'rel="last"'
        )
        self.assertDictEqual(
            pager.pagination_headers(),
            {
                "Link": link,
                "X-Pagination-Current-Page": 5,
                "X-Pagination-Per-Page": 300,
                "X-Pagination-Total-Count": 10000,
            },
        )
        pager.set_paging_info({"page": 50, "per_page": 1000})
        self.assertEqual(pager.pages, 10)
        self.assertEqual(pager.has_prev, True)
        self.assertEqual(pager.has_next, False)
        self.assertEqual(pager.first_item, 49000)
        self.assertEqual(pager.last_item, 10000)
        self.assertEqual(pager.is_valid_page, False)
        link = (
            "</test_ur?per_page=1000&page=1>;"
            + ' rel="first", </test_ur?per_page=1000&page=49>;'
            + ' rel="prev", </test_ur?per_page=1000&page=10>;'
            + ' rel="last"'
        )
        self.assertDictEqual(
            pager.pagination_headers(),
            {
                "Link": link,
                "X-Pagination-Current-Page": 50,
                "X-Pagination-Per-Page": 1000,
                "X-Pagination-Total-Count": 10000,
            },
        )
        pager.set_paging_info({"page": 10, "per_page": 1000})
        self.assertEqual(pager.pages, 10)
        self.assertEqual(pager.has_prev, True)
        self.assertEqual(pager.has_next, False)
        self.assertEqual(pager.first_item, 9000)
        self.assertEqual(pager.last_item, 10000)
        self.assertEqual(pager.is_valid_page, True)
        link = (
            "</test_ur?per_page=1000&page=1>; "
            + 'rel="first", </test_ur?per_page=1000&page=9>; '
            + 'rel="prev", </test_ur?per_page=1000&page=10>; rel="last"'
        )
        self.assertDictEqual(
            pager.pagination_headers(),
            {
                "Link": link,
                "X-Pagination-Current-Page": 10,
                "X-Pagination-Per-Page": 1000,
                "X-Pagination-Total-Count": 10000,
            },
        )

    def test_total_count_setter(self):
        items_count = 1000
        pager = Pagination(items_count, "/test_ur", per_page=10)
        self.assertEqual(pager._total_count, 1000)
        pager.total_count = 100
        self.assertEqual(pager._total_count, 100)
        pager.set_paging_info({"page": 10, "per_page": 0})
        pager.total_count = 10
        self.assertEqual(pager._total_count, 10)

    def test_slice(self):
        items_count = 5
        pager = Pagination(items_count, "/test_ur", page=1, per_page=3)
        test_results = [1, 2, 3, 4, 5]
        self.assertEqual(pager.slice(test_results), [1, 2, 3])
