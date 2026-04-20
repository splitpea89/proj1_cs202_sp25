import unittest
from proj1 import *

class TestRegionFunctions(unittest.TestCase):

    def setUp(self):
        rect = GlobeRect(0.0, 10.0, 0.0, 10.0)
        self.rc = RegionCondition(Region(rect, "Test Region", "other"), 2020, 1000, 5000.0)

        rect_zero = GlobeRect(0.0, 10.0, 0.0, 10.0)
        self.rc_zero = RegionCondition(Region(rect_zero, "Empty Region", "ocean"), 2020, 0, 0.0)

        rect_forest = GlobeRect(0.0, 10.0, 0.0, 10.0)
        self.rc_forest = RegionCondition(Region(rect_forest, "Forest Region", "forest"), 2020, 100000, 5000.0)

        rect_dense = GlobeRect(0.0, 1.0, 0.0, 1.0)
        self.rc_dense = RegionCondition(Region(rect_dense, "Dense Region", "other"), 2020, 999999, 1000.0)

        rect_double = GlobeRect(0.0, 10.0, 0.0, 10.0)
        self.rc_double = RegionCondition(Region(rect_double, "Double Emissions", "other"), 2020, 1000, 10000.0)

        self.rect_dateline = GlobeRect(0.0, 10.0, 170.0, -170.0)
        self.rect_equivalent = GlobeRect(0.0, 10.0, -10.0, 10.0)

        # Large population so int truncation doesn't swallow small growth rates
        rect_large = GlobeRect(0.0, 10.0, 0.0, 10.0)
        self.rc_large = RegionCondition(Region(rect_large, "Large Region", "other"), 2020, 1000000, 5000000.0)

    # emissions_per_capita
    def test_emissions_per_capita_normal(self):
        self.assertAlmostEqual(emissions_per_capita(self.rc), 5.0, places=4)

    def test_emissions_per_capita_zero_pop(self):
        self.assertAlmostEqual(emissions_per_capita(self.rc_zero), 0.0, places=4)

    def test_emissions_per_capita_returns_float(self):
        self.assertIsInstance(emissions_per_capita(self.rc_zero), float)

    def test_emissions_per_capita_type_error(self):
        with self.assertRaises(TypeError):
            emissions_per_capita("not a RegionCondition")  # type: ignore

    # area
    def test_area_positive(self):
        self.assertGreater(area(self.rc.region.rect), 0)

    def test_area_dateline_positive(self):
        self.assertGreater(area(self.rect_dateline), 0)

    def test_area_dateline_equals_equivalent(self):
        self.assertAlmostEqual(area(self.rect_dateline), area(self.rect_equivalent), places=1)

    def test_area_larger_is_bigger(self):
        rect_big = GlobeRect(0.0, 20.0, 0.0, 20.0)
        self.assertGreater(area(rect_big), area(self.rc.region.rect))

    def test_area_type_error(self):
        with self.assertRaises(TypeError):
            area("not a GlobeRect")  # type: ignore

    # emissions_per_square_km
    def test_emissions_per_square_km_positive(self):
        self.assertGreater(emissions_per_square_km(self.rc), 0)

    def test_emissions_per_square_km_proportional(self):
        self.assertAlmostEqual(
            emissions_per_square_km(self.rc_double),
            emissions_per_square_km(self.rc) * 2,
            places=4
        )

    def test_emissions_per_square_km_uses_total(self):
        expected = self.rc.ghg_rate / area(self.rc.region.rect)
        self.assertAlmostEqual(emissions_per_square_km(self.rc), expected, places=4)

    def test_emissions_per_square_km_type_error(self):
        with self.assertRaises(TypeError):
            emissions_per_square_km("not a RegionCondition")  # type: ignore

    # densest
    def test_densest_single(self):
        self.assertEqual(densest([self.rc]), "Test Region")

    def test_densest_picks_denser(self):
        self.assertEqual(densest([self.rc, self.rc_dense]), "Dense Region")

    def test_densest_order_independent(self):
        self.assertEqual(densest([self.rc, self.rc_dense]), densest([self.rc_dense, self.rc]))

    def test_densest_three_regions(self):
        self.assertEqual(densest([self.rc, self.rc_dense, self.rc_forest]), "Dense Region")

    def test_densest_empty_list(self):
        with self.assertRaises(ValueError):
            densest([])

    def test_densest_returns_string(self):
        self.assertIsInstance(densest([self.rc]), str)

    # project_condition
    def test_project_year_advances(self):
        self.assertEqual(project_condition(self.rc, 10).year, 2030)

    def test_project_year_advances_multi(self):
        self.assertEqual(project_condition(self.rc, 50).year, 2070)

    def test_project_other_terrain_grows(self):
        self.assertGreater(project_condition(self.rc_large, 1).pop, self.rc_large.pop)

    def test_project_forest_shrinks(self):
        self.assertLess(project_condition(self.rc_forest, 1).pop, self.rc_forest.pop)

    def test_project_emissions_scale_with_pop(self):
        projected = project_condition(self.rc_large, 1)
        expected_ratio = projected.pop / self.rc_large.pop
        actual_ratio = projected.ghg_rate / self.rc_large.ghg_rate
        self.assertAlmostEqual(actual_ratio, expected_ratio, places=4)

    def test_project_region_unchanged(self):
        self.assertEqual(project_condition(self.rc, 5).region, self.rc.region)

    def test_project_returns_region_condition(self):
        self.assertIsInstance(project_condition(self.rc, 1), RegionCondition)

    def test_project_type_error_rc(self):
        with self.assertRaises(TypeError):
            project_condition("not a RegionCondition", 5)  # type: ignore

    def test_project_type_error_years(self):
        with self.assertRaises(TypeError):
            project_condition(self.rc, 1.5)  # type: ignore

    def test_project_invalid_years(self):
        with self.assertRaises(ValueError):
            project_condition(self.rc, 0)

    # region_conditions list
    def test_region_conditions_has_four(self):
        self.assertEqual(len(region_conditions), 4)

    def test_region_conditions_all_correct_type(self):
        for rc in region_conditions:
            self.assertIsInstance(rc, RegionCondition)

    def test_region_conditions_unique_names(self):
        names = [rc.region.name for rc in region_conditions]
        self.assertEqual(len(names), len(set(names)))


if __name__ == '__main__':
    unittest.main()