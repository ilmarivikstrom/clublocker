from invoke import task
from datetime import datetime
import glob

@task
def clean(c):
    files = glob.glob(f'./data/*{str(datetime.now().date())}*')
    for file in files:
        print(f'Deleting file {file}')
        c.run(f'rm {file}')