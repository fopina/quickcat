from flask import Flask, render_template, jsonify, request, abort
import mongoengine
import os
from . import models


app = Flask(__name__)
# TODO tweak for heroku, make this configurable in a settings file
app.config['MONGODB_HOST'] = os.getenv('MONGODB_URI', 'localhost')
models.db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html', categories=models.Category.objects.all())


@app.route('/stats/')
@app.route('/stats')
def stats():
    data = []
    for cat in models.Category.objects.all():
        data.append({
            'name': cat.name,
            'size': models.Image.objects.filter(**{
                'category_votes__%s__gte' % cat.name: 0
            }).count(),
        })

    other=[
        {
            'id': 'uncat',
            'name': 'Uncategorized',
            'size': models.Image.objects.filter(
                category_votes=None
            ).count(),
        },
        {
            'id': 'total',
            'name': 'Total images',
            'size': models.Image.objects.count(),
        }
    ]

    if request.args.get('format') == 'json':
        return jsonify(dict(
            categories=data,
            other=other
        ))
    else:
        return render_template(
            'stats.html',
            categories=data,
            other=other
        )


@app.route('/stats/<name>')
def stats_category(name):
    category = models.Category.objects.filter(name=name).first()
    if category is None:
        abort(404)
    images=models.Image.objects.filter(**{
        'category_votes__%s__gte' % category.name: 0
    })
    if request.args.get('format') == 'json':
        return jsonify(
            category=category,
            images=images
        )
    else:
        return render_template(
            'stats_category.html',
            category=category,
            images=images
        )


@app.route('/stats/o/<cid>')
def stats_uncategory(cid):
    if cid == 'total':
        category = 'Total images'
        images = models.Image.objects.all()
    elif cid == 'uncat':
        category = 'Uncategorized'
        images = models.Image.objects.filter(category_votes=None)
    else:
        abort(404)

    if request.args.get('format') == 'json':
        return jsonify(
            category={'name': category},
            images=images
        )
    else:
        return render_template(
            'stats_category.html',
            category={'name': category},
            images=images
        )


@app.route('/api/more')
def api_more():
    return jsonify(models.Image.objects.order_by('reviews')[:3])


@app.route('/api/vote', methods=['POST'])
def api_vote():
    category = models.Category.objects.filter(name=request.form.get('category')).first()
    image = models.Image.objects.filter(url=request.form.get('url')).first()
    
    if category and image:
        image.update(**{
            # ninja style to be able to increment categories with spaces
            # HACKER WARNING: this might look like a good injection point
            # but categories are created manually and I am sure there are better
            # eggs to hunt in the rest of this unsafe code!
            'inc__category_votes__%s' % category.name: 1,
            'inc__reviews': 1
        })
        return jsonify(models.Image.objects.order_by('reviews')[:3])
    else:
        return jsonify({}), 400



