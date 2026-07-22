from scholaros.plugins import Plugin
from scholaros.plugins import PluginManager
from scholaros.plugins import PluginManifest


class DummyPlugin(Plugin):

    manifest = PluginManifest(
        name="dummy",
        version="1.0",
        author="ScholarOS",
        description="Dummy plugin",
        scholaros=">=0.1.0",
        license="Apache-2.0",
    )

    def install(self):
        pass

    def uninstall(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass


def test_plugin_registration():

    manager = PluginManager()

    plugin = DummyPlugin()

    manager.register(plugin)

    assert "dummy" in manager.installed()