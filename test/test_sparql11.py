
from rdflib import ConjunctiveGraph, URIRef

import unittest

# this assumed SPARQL1.1 query/update endpoints
# running locally at localhost:3030/data
# for instance fuseki started with ./fuseki-server --mem --update /data

# THIS WILL DELETE ALL DATA IN THE /data dataset

michel = URIRef(u'urn:michel')
tarek = URIRef(u'urn:tarek')
bob = URIRef(u'urn:bob')
likes = URIRef(u'urn:likes')
hates = URIRef(u'urn:hates')
pizza = URIRef(u'urn:pizza')
cheese = URIRef(u'urn:cheese')

graphuri = URIRef('urn:graph')
othergraphuri = URIRef('urn:othergraph')


class TestSparql11(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.graph = ConjunctiveGraph('SPARQLUpdateStore')

        root = "http://localhost:3030/data/"
        self.graph.open((root + "query", root + "update"))

        # clean out the store
        for c in self.graph.contexts():
            c.remove((None, None, None))

    def tearDown(self):
        self.graph.close()

    def testSimpleGraph(self):
        g = self.graph.get_context(graphuri)
        g.add((tarek, likes, pizza))
        g.add((bob, likes, pizza))
        g.add((bob, likes, cheese))

        g2 = self.graph.get_context(othergraphuri)
        g2.add((michel, likes, pizza))

        self.assertEquals(3, len(g), 'graph contains 3 triples')
        self.assertEquals(1, len(g2), 'other graph contains 1 triple')

        r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(2, len(list(r)), "two people like pizza")

        r = g.triples((None, likes, pizza))
        self.assertEquals(2, len(list(r)), "two people like pizza")

        # Test initBindings
        r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
                    initBindings={'s': tarek})
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = g.triples((tarek, likes, pizza))
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = g.triples((tarek, likes, cheese))
        self.assertEquals(0, len(list(r)), "tarek doesn't like cheese")

        g2.add((tarek, likes, pizza))
        g.remove((tarek, likes, pizza))
        r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(1, len(list(r)), "only bob likes pizza")

    def testConjunctiveDefault(self):
        g = self.graph.get_context(graphuri)
        g.add((tarek, likes, pizza))
        g2 = self.graph.get_context(othergraphuri)
        g2.add((bob, likes, pizza))
        g.add((tarek, hates, cheese))

        self.assertEquals(2, len(g), 'graph contains 2 triples')
        self.assertEquals(3, len(self.graph),
                            'default union graph contains three triples')

        r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(2, len(list(r)), "two people like pizza")

        r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
                            initBindings={'s': tarek})
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = self.graph.triples((tarek, likes, pizza))
        self.assertEquals(1, len(list(r)), "i was asking only about tarek")

        r = self.graph.triples((tarek, likes, cheese))
        self.assertEquals(0, len(list(r)), "tarek doesn't like cheese")

        g2.remove((bob, likes, pizza))

        r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
        self.assertEquals(1, len(list(r)), "only tarek likes pizza")

from nose import SkipTest
import urllib2
try:
    assert len(urllib2.urlopen("http://localhost:3030/data/").read()) > 0
except:
    raise SkipTest("http://localhost:3030/data/ is unavailable.")


if __name__ == '__main__':
    unittest.main()
