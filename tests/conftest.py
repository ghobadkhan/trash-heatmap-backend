import pytest
import os
import sys
from time import sleep
from docker.models.containers import Container
from docker import DockerClient
from typing import cast
from src.app import create_app


def run_container(docker_base_url:str) -> Container:
    if docker_base_url =='env':
        # if env (default) is provided, it means that address to docker host is in the environment
        # variables. This must be set in .env, key: DOCKER_HOST
        if "DOCKER_HOST" in os.environ:
            client = DockerClient.from_env()
        else:
            raise ValueError("The value of 'DOCKER_HOST' is not set in .env file!")
    else:
        client = DockerClient(base_url=docker_base_url)
    container = client.containers.run(
        image='postgres:latest',
        name='test_db',
        remove=True,
        ports={'5432/tcp': 10000},
        environment={
            'POSTGRES_PASSWORD': '123456',
            'POSTGRES_DB': 'test_trash_heat'
        },
        mem_limit='500m',
        detach=True
    )
    container = cast(Container,container)
    attempts = 0
    while attempts < 5:
        attempts += 1
        sleep(1)
        container.reload()
        if container.status == 'running':
            break
    else:
        raise Exception('DB container start Timeout')
    return container

# pytest -s --db_docker_url 'unix:///home/arian/.docker/desktop/docker.sock'
def pytest_addoption(parser):
    parser.addoption("--db_docker_url", action="store", default="env")

@pytest.fixture(scope='session')
def app(pytestconfig):
    db_docker_url = pytestconfig.getoption('db_docker_url')
    print(db_docker_url)
    app,socketio = create_app()
    db_container = run_container(db_docker_url)
    app.config.update({
        "TESTING": True
    })
    yield app,socketio
    db_container.stop()

@pytest.fixture(scope='session')
def client(app):
    app = app[0]
    yield app.test_client()

@pytest.fixture(scope='session')
def socket_client(app):
    socketio = app[1]
    yield socketio.test_client(app[0])

@pytest.fixture(scope='session')
def user(app):
    app = app[0]
    with app.app_context():
        from src.app.controller import create_user, create_all_tables
        create_all_tables()
        user = create_user(
            email="test@email.com",
            first_name='Test Name',
            last_name='Test Family',
            passwd='123456'
        )
        yield user

