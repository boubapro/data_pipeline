import unittest
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment

MACRO = Path(__file__).parent.parent / "macros" / "generate_schema_name.sql"


def render(target_name, custom_schema, target_schema="MY_SCHEMA"):
    env = Environment()
    template = env.from_string(
        MACRO.read_text(encoding="utf-8")
        + "{{ generate_schema_name(custom, none) }}"
    )
    target = SimpleNamespace(name=target_name, schema=target_schema)
    return template.render(target=target, custom=custom_schema).strip()


class GenerateSchemaNameTests(unittest.TestCase):
    def test_prod_keeps_custom_schema_name(self):
        self.assertEqual(
            render("prod", "datamart_sales_feed"), "DATAMART_SALES_FEED"
        )

    def test_non_prod_targets_are_prefixed(self):
        self.assertEqual(
            render("dev", "datamart_sales_feed"), "DEV_DATAMART_SALES_FEED"
        )
        self.assertEqual(
            render("int", "datamart_sales_feed"), "INT_DATAMART_SALES_FEED"
        )

    def test_environments_never_share_a_schema(self):
        names = {render(t, "datamart_sales_feed") for t in ("dev", "int", "prod")}
        self.assertEqual(len(names), 3)

    def test_without_custom_schema_uses_target_schema(self):
        for target in ("dev", "int", "prod"):
            self.assertEqual(render(target, None, "RAW_X"), "RAW_X")

    def test_prefixed_feed_schema_still_maps_to_bi_schema(self):
        # safe_bi_swap retire le suffixe _FEED : le préfixe doit être conservé
        feed = render("dev", "datamart_sales_feed")
        self.assertTrue(feed.endswith("_FEED"))
        self.assertEqual(feed[:-5], "DEV_DATAMART_SALES")


if __name__ == "__main__":
    unittest.main()
