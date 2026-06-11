import os

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
    assert isinstance(nconf.things, list)
    assert len(nconf.things) == 3
    assert nconf.overriden == "True"


@pytest.mark.parametrize(
    "set_envars", [("simple_overriden", '{"a": 1, "b": 2}')], indirect=True
)
def test_json_envar(set_envars):
    nconf = NC("tests/data/simple.nconf")
    assert isinstance(nconf.overriden, NC)
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


def test_dotted_attribute_access():
    """Test that top-level config items support both dict and attribute access."""
    nconf = NC("tests/data/simple.nconf")

    # Dictionary access
    assert nconf["key"] == "value"
    assert nconf["test"] == 1
    assert nconf["overriden"] is False

    # Attribute access (dotted notation)
    assert nconf.key == "value"
    assert nconf.test == 1
    assert nconf.overriden is False

    # Both should return the same values
    assert nconf["key"] == nconf.key
    assert nconf["test"] == nconf.test
    assert nconf["overriden"] == nconf.overriden


def test_nested_dotted_attribute_access():
    """Test that nested config items support both dict and attribute access."""
    nconf = NC("tests/data/nested.nconf")

    # Top-level access (both methods)
    assert nconf["test"] == nconf.test == "value"

    # Nested access
    assert nconf["top"]["v1"] == nconf.top.v1 == 1
    assert nconf["top"]["middle"]["v2"] == nconf.top.middle.v2 == 2
    assert nconf["top"]["middle"]["lowest"]["v3"] == nconf.top.middle.lowest.v3 == 3


def test_imported_config_dotted_access():
    """Test that imported configs support both dict and attribute access."""
    nconf = NC("tests/data/nested.nconf")

    # Imported config access
    assert nconf["animals"]["dog"]["name"] == nconf.animals.dog.name == "Dog"
    assert nconf["animals"]["dog"]["diet"] == nconf.animals.dog.diet == "Omnivore"
    assert nconf["animals"]["panda"]["diet"] == nconf.animals.panda.diet == "Herbivore"

    # Mixed access patterns
    assert nconf.animals["dog"].name == "Dog"
    assert nconf["animals"].dog.name == "Dog"


def test_to_dict_conversion():
    """Test that to_dict() recursively converts NanoConf to plain dicts."""
    nconf = NC("tests/data/nested.nconf")

    # Convert to plain dict
    plain_dict = nconf.to_dict()

    # Verify it's a plain dict, not NanoConf
    assert isinstance(plain_dict, dict)
    assert not isinstance(plain_dict, NC)

    # Verify nested structures are also plain dicts
    assert isinstance(plain_dict["top"], dict)
    assert not isinstance(plain_dict["top"], NC)
    assert isinstance(plain_dict["top"]["middle"], dict)
    assert not isinstance(plain_dict["top"]["middle"], NC)

    # Verify values are preserved
    assert plain_dict["test"] == "value"
    assert plain_dict["top"]["v1"] == 1
    assert plain_dict["top"]["middle"]["v2"] == 2

    # Verify animals sub-config
    animals_dict = nconf.animals.to_dict()
    assert isinstance(animals_dict["dog"], dict)
    assert not isinstance(animals_dict["dog"], NC)
    assert animals_dict["dog"]["name"] == "Dog"
