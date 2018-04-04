import click
from .routes import app
from . import models


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
            models.Image.objects.insert(imgs, write_concern={'continue_on_error': True})
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