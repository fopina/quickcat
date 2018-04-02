import click
from flask import Flask, render_template, jsonify, request
import mongoengine
from . import app, models


@app.route('/')
def index():
    return render_template('index.html', categories=models.Category.objects.all())


@app.route('/api/more')
def api_more():
    return jsonify(models.Image.objects.order_by('reviews')[:3])


@app.route('/api/vote', methods=['POST'])
def api_vote():
    category = models.Category.objects.filter(name=request.form.get('category')).first()
    image = models.Image.objects.filter(url=request.form.get('url')).first()
    
    if category and image:
        # TODO atomify this
        if not image.reviews:  # cover None case
            image.reviews = 1
        else:
            image.reviews += 1
        if image.category_votes:
            # TODO needs to be a copy to be marked as changed...
            # https://github.com/MongoEngine/mongoengine/issues/889
            m = image.category_votes.copy()
        else:
            m = {}
        m[category.name] = m.get(category.name, 0) + 1
        image.category_votes = m
        image.save()
        return jsonify(models.Image.objects.order_by('reviews')[:3])
    else:
        return jsonify({}), 400


@app.cli.command()
@click.argument('infile')
def load_file(infile):
    cnt = [0, 0]
    with open(infile, 'r') as inp:
        for url in inp:
            try:
                models.Image(url=url.strip()).save()
                cnt[0] += 1
            except models.errors.NotUniqueError:
                cnt[1] += 1
    click.echo('%d added, %d already existed' % tuple(cnt))


@app.cli.command()
@click.argument('category', nargs=-1)
def categories(category):
    click.echo('Existing categories will be removed and these will be added')
    click.echo(', '.join(category))
    if not click.confirm('Continue?'):
        return

    models.Category.objects.all().delete()
    for c in category:
        models.Category(name=c).save()
    click.echo('Categories recreated')
