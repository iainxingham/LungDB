# LungDB

Scripts for lung function database

### Setting up the development environment

Setting up the various bits not checked in to version control

```sh
python3 -m venv venv
source ./venv/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install -r requirements-dev.txt
mkdir data
mkdir logs
alembic upgrade head
```