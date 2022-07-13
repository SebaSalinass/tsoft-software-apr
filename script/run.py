import os
import subprocess
import click

from flask_migrate import Migrate

from app import create_app
from app.db import db
from app.utils.formaters import _T, _M, _R


app = create_app(os.getenv('FLASK_ENV', 'development'))
migrate = Migrate(app, db)


@app.context_processor
def inject_formaters() -> dict:
    """Injects utils formaters for RUT, Money and Dates into the 
    context procesor

    Returns:
        dict: Objects dict to be injected
    """
    return dict(_T=_T, _M=_M, _R=_R)

@app.cli.command(name='test', with_appcontext=False)
@click.option('--html/--no-html', default=False)
@click.option('--v/--no-v', default=False)
def tests(html: bool = False, v: bool = False) -> None:
    """ Run the unit tests. """

    subprocess.Popen([
        'pytest', 'tests', '--cov=app', 
        ["","--cov-report=html"][html],
        ["","-v"][v],               
        ], shell=True)
    return
