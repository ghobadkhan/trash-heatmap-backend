import pytest
from time import sleep
from docker.models.containers import Container
from docker import DockerClient
from typing import cast
from src import create_app


def run_container(docker_base_url='unix:///home/arian/.docker/desktop/docker.sock') -> Container:
    if docker_base_url =='env':
        client = DockerClient.from_env()
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
    db_container = run_container(db_docker_url)
    app = create_app(env='Test')
    app.config.update({
        "TESTING": True
    })
    yield app
    db_container.stop()

@pytest.fixture(scope='session')
def client(app):
    yield app.test_client()

@pytest.fixture(scope='session')
def user(app):
    with app.app_context():
        from src.controller import create_user, create_all_tables, session
        create_all_tables()
        user = create_user(
            email="sag@email.com",
            first_name='Kian khan',
            last_name='mostaravi',
            passwd='123456'
        )
        yield user
        session.close()
