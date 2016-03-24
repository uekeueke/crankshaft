import unittest
import numpy as np

import unittest


# from mock_plpy import MockPlPy
# plpy = MockPlPy()
#
# import sys
# sys.modules['plpy'] = plpy
from helper import plpy, fixture_file

import crankshaft.clustering as cc
from crankshaft import random_seeds
import json

class MoranTest(unittest.TestCase):
    """Testing class for Moran's I functions."""

    def setUp(self):
        plpy._reset()
        self.params = {"id_col": "cartodb_id",
                       "attr1": "andy",
                       "attr2": "jay_z",
                       "subquery": "SELECT * FROM a_list",
                       "geom_col": "the_geom",
                       "num_ngbrs": 321}
        self.params_markov = {"id_col": "cartodb_id",
                              "time_cols": ["_2013_dec", "_2014_jan", "_2014_feb"],
                              "subquery": "SELECT * FROM a_list",
                              "geom_col": "the_geom",
                              "num_ngbrs": 321}
        self.neighbors_data = json.loads(open(fixture_file('neighbors.json')).read())
        self.moran_data = json.loads(open(fixture_file('moran.json')).read())

    def test_map_quads(self):
        """Test map_quads."""
        self.assertEqual(cc.map_quads(1), 'HH')
        self.assertEqual(cc.map_quads(2), 'LH')
        self.assertEqual(cc.map_quads(3), 'LL')
        self.assertEqual(cc.map_quads(4), 'HL')
        self.assertEqual(cc.map_quads(33), None)
        self.assertEqual(cc.map_quads('andy'), None)

    def test_query_attr_select(self):
        """Test query_attr_select."""

        ans = "i.\"andy\"::numeric As attr1, " \
              "i.\"jay_z\"::numeric As attr2, "

        self.assertEqual(cc.query_attr_select(self.params), ans)

    def test_query_attr_where(self):
        """Test query_attr_where."""

        ans = "idx_replace.\"andy\" IS NOT NULL AND "\
              "idx_replace.\"jay_z\" IS NOT NULL AND "\
              "idx_replace.\"jay_z\" <> 0"

        self.assertEqual(cc.query_attr_where(self.params), ans)

    def test_knn(self):
        """Test knn function."""

        ans = "SELECT i.\"cartodb_id\" As id, i.\"andy\"::numeric As attr1, " \
              "i.\"jay_z\"::numeric As attr2, (SELECT ARRAY(SELECT j.\"cartodb_id\" " \
              "FROM (SELECT * FROM a_list) As j WHERE j.\"andy\" IS NOT NULL AND " \
              "j.\"jay_z\" IS NOT NULL AND j.\"jay_z\" <> 0 ORDER BY " \
              "j.\"the_geom\" <-> i.\"the_geom\" ASC LIMIT 321 OFFSET 1 ) ) " \
              "As neighbors FROM (SELECT * FROM a_list) As i WHERE i.\"andy\" IS NOT " \
              "NULL AND i.\"jay_z\" IS NOT NULL AND i.\"jay_z\" <> 0 ORDER " \
              "BY i.\"cartodb_id\" ASC;"

        ans_markov = "SELECT i.\"cartodb_id\" As id, " \
              "i.\"_2013_dec\"::numeric As attr1, " \
              "i.\"_2014_jan\"::numeric As attr2, " \
              "i.\"_2014_feb\"::numeric As attr3, " \
              "(SELECT ARRAY(SELECT j.\"cartodb_id\" " \
                            "FROM (SELECT * FROM a_list) As j " \
                            "WHERE j.\"_2013_dec\" IS NOT NULL AND " \
                                  "j.\"_2014_jan\" IS NOT NULL AND " \
                                  "j.\"_2014_feb\" IS NOT NULL " \
                            "ORDER BY j.\"the_geom\" <-> i.\"the_geom\" ASC " \
                            "LIMIT 321 OFFSET 1 ) ) As neighbors " \
              "FROM (SELECT * FROM a_list) As i " \
              "WHERE i.\"_2013_dec\" IS NOT NULL AND " \
                    "i.\"_2014_jan\" IS NOT NULL AND " \
                    "i.\"_2014_feb\" IS NOT NULL "\
              "ORDER BY i.\"cartodb_id\" ASC;"

        self.assertEqual(cc.knn(self.params), ans)

        self.assertEqual(cc.knn(self.params_markov), ans_markov)

    def test_queen(self):
        """Test queen neighbors function."""

        ans = "SELECT i.\"cartodb_id\" As id, i.\"andy\"::numeric As attr1, " \
              "i.\"jay_z\"::numeric As attr2, (SELECT ARRAY(SELECT " \
              "j.\"cartodb_id\" FROM (SELECT * FROM a_list) As j WHERE ST_Touches(" \
              "i.\"the_geom\", j.\"the_geom\") AND j.\"andy\" IS NOT NULL " \
              "AND j.\"jay_z\" IS NOT NULL AND j.\"jay_z\" <> 0)) As " \
              "neighbors FROM (SELECT * FROM a_list) As i WHERE i.\"andy\" IS NOT NULL " \
              "AND i.\"jay_z\" IS NOT NULL AND i.\"jay_z\" <> 0 ORDER BY " \
              "i.\"cartodb_id\" ASC;"

        self.assertEqual(cc.queen(self.params), ans)

    def test_get_query(self):
        """Test get_query."""

        ans = "SELECT i.\"cartodb_id\" As id, i.\"andy\"::numeric As attr1, " \
              "i.\"jay_z\"::numeric As attr2, (SELECT ARRAY(SELECT " \
              "j.\"cartodb_id\" FROM (SELECT * FROM a_list) As j WHERE j.\"andy\" IS " \
              "NOT NULL AND j.\"jay_z\" IS NOT NULL AND j.\"jay_z\" <> 0 " \
              "ORDER BY j.\"the_geom\" <-> i.\"the_geom\" ASC LIMIT 321 " \
              "OFFSET 1 ) ) As neighbors FROM (SELECT * FROM a_list) As i WHERE " \
              "i.\"andy\" IS NOT NULL AND i.\"jay_z\" IS NOT NULL AND " \
              "i.\"jay_z\" <> 0 ORDER BY i.\"cartodb_id\" ASC;"

        self.assertEqual(cc.get_query('knn', self.params), ans)

    def test_get_attributes(self):
        """Test get_attributes."""

        ## need to add tests

        self.assertEqual(True, True)

    def test_get_weight(self):
        """Test get_weight."""
        ## need to add tests

        self.assertEqual(True, True)


    def test_quad_position(self):
        """Test lisa_sig_vals."""

        quads = np.array([1, 2, 3, 4], np.int)

        ans = np.array(['HH', 'LH', 'LL', 'HL'])
        test_ans = cc.quad_position(quads)

        self.assertTrue((test_ans == ans).all())

    def test_moran_local(self):
        """Test Moran's I local"""
        data = [ { 'id': d['id'], 'attr1': d['value'], 'neighbors': d['neighbors'] } for d in self.neighbors_data]
        plpy._define_result('select', data)
        random_seeds.set_random_seeds(1234)
        result = cc.moran_local('table', 'value', 0.05, 5, 99, 'the_geom', 'cartodb_id', 'knn')
        result = [(row[0], row[1]) for row in result]
        expected = self.moran_data
        for ([res_val, res_quad], [exp_val, exp_quad]) in zip(result, expected):
            self.assertAlmostEqual(res_val, exp_val)
            self.assertEqual(res_quad, exp_quad)

    def test_moran_local_rate(self):
        """Test Moran's I rate"""
        data = [ { 'id': d['id'], 'attr1': d['value'], 'attr2': 1, 'neighbors': d['neighbors'] } for d in self.neighbors_data]
        plpy._define_result('select', data)
        random_seeds.set_random_seeds(1234)
        result = cc.moran_local_rate('table', 'numerator', 'denominator', 0.05, 5, 99, 'the_geom', 'cartodb_id', 'knn')
        result = [(row[0], row[1]) for row in result]
        expected = self.moran_data
        for ([res_val, res_quad], [exp_val, exp_quad]) in zip(result, expected):
            self.assertAlmostEqual(res_val, exp_val)
