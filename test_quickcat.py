#!/usr/bin/env python

import unittest
import json
import re

# UGLY WARNING: refactor app setup to make this prettier
import os
os.environ['MONGODB_URI'] = 'mongomock://localhost/test'

import quickcat.routes  # load routes
quickcat.routes.app.config['TESTING'] = True
from quickcat.models import Image, Category, db


class QuickCatTestCase(unittest.TestCase):

    def setUp(self):
        self.app = quickcat.routes.app.test_client()

    def tearDown(self):
        with quickcat.routes.app.app_context():
            db.connection.drop_database('test')

    def test_index(self):
        res = self.app.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('<div class="card mb-4 box-shadow" id="id_image_0">', html)
        self.assertIn('<div class="card mb-4 box-shadow" id="id_image_1">', html)
        self.assertIn('<div class="card mb-4 box-shadow" id="id_image_2">', html)
        self.assertNotIn('<div class="card mb-4 box-shadow" id="id_image_3">', html)

    def test_api_more(self):
        res = self.app.get('/api/more')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.get_data(as_text=True)), [])
        Image.objects.insert([
            Image(url='a'),
            Image(url='b'),
            Image(url='c'),
            Image(url='d', reviews=1),
        ])
        res = self.app.get('/api/more')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        for d in data:
            del(d['_id'])
        self.assertEqual(data, [{'url': 'a'}, {'url': 'b'}, {'url': 'c'}])
        Image.objects.filter(url='a').update(reviews=2)
        res = self.app.get('/api/more')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        for d in data:
            del(d['_id'])
        self.assertEqual(data, [{'url': 'b'}, {'url': 'c'}, {'url': 'd', 'reviews': 1}])

    def test_api_vote(self):
        Category.objects.insert([
            Category(name='yes sir'),  # test space in name
            Category(name='nope'),
        ])
        Image.objects.insert([
            Image(url='a'),
            Image(url='b'),
            Image(url='c')
        ])
        res = self.app.get('/api/vote')
        self.assertEqual(res.status_code, 405)  # GET not allowed

        res = self.app.post('/api/vote', data={'category': 'nope', 'url': 'a'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Image.objects.filter(url='a').first().reviews, 1)
        self.assertEqual(Image.objects.filter(url='a').first().category_votes, {'nope': 1})
        # nothing else changed...
        self.assertIsNone(Image.objects.filter(url='b').first().reviews)
        self.assertIsNone(Image.objects.filter(url='b').first().category_votes)

        # incrementing again
        res = self.app.post('/api/vote', data={'category': 'nope', 'url': 'a'})
        self.assertEqual(res.status_code, 200)
        res = self.app.post('/api/vote', data={'category': 'yes sir', 'url': 'a'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Image.objects.filter(url='a').first().reviews, 3)
        self.assertEqual(Image.objects.filter(url='a').first().category_votes, {'nope': 2, 'yes sir': 1})

        res = self.app.post('/api/vote', data={'category': 'invalid', 'url': 'a'})
        self.assertEqual(res.status_code, 400)
        res = self.app.post('/api/vote', data={'category': 'nope', 'url': 'invalid'})
        self.assertEqual(res.status_code, 400)

    def test_stats(self):
        res = self.app.get('/stats')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<p class="card-text">(.*?)</p>.*?<span class="review_number">(\d+)</span> items</small>', res.get_data(as_text=True), re.S),
            [('Uncategorized', '0'), ('Total images', '0')]
        )
        Category.objects.insert([
            Category(name='catA'),
            Category(name='catB'),
        ])
        Image.objects.insert([
            Image(url='a'),
            Image(url='b'),
            Image(url='c')
        ])
        res = self.app.get('/stats')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<p class="card-text">(.*?)</p>.*?<span class="review_number">(\d+)</span> items</small>', res.get_data(as_text=True), re.S),
            [('catA', '0'), ('catB', '0'), ('Uncategorized', '3'), ('Total images', '3')]
        )
        
        Image.objects.filter(url='a').update(inc__category_votes__catA=1, inc__reviews=1)
        res = self.app.get('/stats')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<p class="card-text">(.*?)</p>.*?<span class="review_number">(\d+)</span> items</small>', res.get_data(as_text=True), re.S),
            [('catA', '1'), ('catB', '0'), ('Uncategorized', '2'), ('Total images', '3')]
        )

        res = self.app.get('/stats/invalid')
        self.assertEqual(res.status_code, 404)

        res = self.app.get('/stats/catA')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<img class="card-img-top" src="(.*?)" alt="Card image cap">.*?<small class="text-muted"><span class="review_number">(\d+)</span> reviews</small>', res.get_data(as_text=True), re.S),
            [('a', '1')]
        )
        res = self.app.get('/stats/catB')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<img class="card-img-top" src="(.*?)" alt="Card image cap">.*?<small class="text-muted"><span class="review_number">(\d+)</span> reviews</small>', res.get_data(as_text=True), re.S),
            []
        )
        res = self.app.get('/stats/o/invalid')
        self.assertEqual(res.status_code, 404)

        res = self.app.get('/stats/o/total')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<img class="card-img-top" src="(.*?)" alt="Card image cap">.*?<small class="text-muted"><span class="review_number">(\d+)</span> reviews</small>', res.get_data(as_text=True), re.S),
            [('a', '1'), ('b', '0'), ('c', '0')]
        )

        res = self.app.get('/stats/o/uncat')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            re.findall('<img class="card-img-top" src="(.*?)" alt="Card image cap">.*?<small class="text-muted"><span class="review_number">(\d+)</span> reviews</small>', res.get_data(as_text=True), re.S),
            [('b', '0'), ('c', '0')]
        )




if __name__ == '__main__':
    unittest.main()