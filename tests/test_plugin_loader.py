from scholaros.plugins.loader import PluginLoader


def create_loader() -> PluginLoader:

    return PluginLoader()


def test_loader_starts_empty():

    loader = create_loader()

    assert loader.loaded == {}
    assert not loader.contains("dummy")


def test_unload_unknown_plugin():

    loader = create_loader()

    loader.unload("dummy")

    assert loader.loaded == {}


def test_clear():

    loader = create_loader()

    loader.loaded["dummy"] = object()

    loader.clear()

    assert loader.loaded == {}


def test_contains():

    loader = create_loader()

    loader.loaded["dummy"] = object()

    assert loader.contains("dummy")
    assert not loader.contains("missing")


def test_get():

    loader = create_loader()

    plugin = object()

    loader.loaded["dummy"] = plugin

    assert loader.get("dummy") is plugin


def test_repr_empty():

    loader = create_loader()

    assert repr(loader) == "PluginLoader(plugins=0)"


def test_repr_loaded():

    loader = create_loader()

    loader.loaded["dummy"] = object()

    assert repr(loader) == "PluginLoader(plugins=1)"


def test_discover_plugins():

    loader = create_loader()

    discovered = loader.discover("scholaros.plugins")

    assert isinstance(discovered, list)


def test_load_invalid_module():

    loader = create_loader()

    try:
        loader.load("scholaros.plugins")
    except LookupError:
        pass
    else:
        assert False, "Expected LookupError"


def test_reload_invalid_module():

    loader = create_loader()

    try:
        loader.reload("scholaros.plugins")
    except LookupError:
        pass
    else:
        assert False, "Expected LookupError"