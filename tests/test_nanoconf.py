import os

from box import Box, BoxList
import pytest

from nanoconf import NC


@pytest.fixture
def set_envars(request):
    if isinstance(request.param, list):
        for pair in request.param:
            os.environ[pair[0]] = pair[1]
        yield
        for pair in request.param:
            del os.environ[pair[0]]
    else:
        os.environ[request.param[0]] = request.param[1]
        yield
        del os.environ[request.param[0]]


@pytest.mark.parametrize("set_envars", [("simple_overriden", "True")], indirect=True)
def test_simple(set_envars):
    nconf = NC("tests/data/simple.nconf")
    assert nconf._name == "simple"
    assert nconf._envar_prefix == "simple"
    assert isinstance(nconf.things, BoxList)
    assert len(nconf.things) == 3
    assert nconf.overriden == "True"


@pytest.mark.parametrize("set_envars", [("simple_overriden", '{"a": 1, "b": 2}')], indirect=True)
def test_json_envar(set_envars):
    nconf = NC("tests/data/simple.nconf")
    assert isinstance(nconf.overriden, Box)
    assert nconf.overriden.a == 1
    assert nconf.overriden.b == 2


def test_nested():
    nconf = NC("tests/data/nested.nconf")
    assert nconf._name == "nested"
    assert nconf.top.v1 == 1
    assert nconf.top.middle.v2 == 2
    assert nconf.top.middle.lowest.v3 == 3
    assert nconf.animals.panda.diet == "Herbivore"
    assert all([nconf.animals.dog, nconf.animals.lion, nconf.animals.penguin])


@pytest.mark.parametrize("set_envars", [("testdog_diet", "Treats!")], indirect=True)
def test_nested_envar(set_envars):
    nconf = NC("tests/data/nested.nconf")
    assert nconf.animals.dog.diet == "Treats!"
