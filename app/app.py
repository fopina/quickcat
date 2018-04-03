import click
from flask import Flask, render_template, jsonify, request, abort
import mongoengine
from . import app, models


@app.route('/')
def index():
    return render_template('index.html', categories=models.Category.objects.all())


@app.route('/stats')
@app.route('/stats/')
def stats():
    data = []
    for cat in models.Category.objects.all():
        data.append({
            'name': cat.name,
            'size': models.Image.objects.filter(**{
                'category_votes__%s__gte' % cat.name: 0
            }).count(),
        })

    return render_template(
        'stats.html',
        categories=data,
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
    )


@app.route('/stats/<name>')
def stats_category(name):
    category = models.Category.objects.filter(name=name).first()
    if category is None:
        abort(404)
    return render_template(
        'stats_category.html',
        category=category,
        images=models.Image.objects.filter(**{
                'category_votes__%s__gte' % category.name: 0
        })
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


@app.cli.command()
@click.option('-b', '--bulk', is_flag=True)
@click.argument('infile', type=click.File('r'))
def load_file(infile, bulk):
    if bulk:
        # better but no stats on inserted records because of possible duplicates...
        imgs = [
            models.Image(url=url.strip())
            for url in infile
        ]
        c_b = models.Image.objects.count()
        try:
            models.Image.objects.insert(imgs, write_concern={'continue_on_error': False})
        except models.errors.NotUniqueError as e:
            pass
        c_f = models.Image.objects.count()
        click.echo('%d added' % (c_f - c_b))
    else:
        cnt = [0, 0]
        for url in infile:
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
