from batou.conftest import root
from batou.lib.file import Directory
from batou_scm.buildout import Buildout
from batou_scm.source import Source
import ConfigParser
import StringIO
import pytest


@pytest.fixture
def buildout(root):
    root.component += Source(
        dist_sources=repr([
            'https://example.com/foo',
            'https://example.com/bar',
        ]))
    root.component += Buildout()
    root.component.configure()
    return root.component._


def read_config(content):
    config = ConfigParser.ConfigParser()
    config.readfp(StringIO.StringIO(content))
    return config


def test_buildout_depends_on_dist_clones(buildout):
    dist_clones = buildout.source.distributions.values()
    assert set(dist_clones).issubset(buildout.sub_components)


def test_dist_paths_are_listed_as_develop_paths_in_overrides(buildout):
    config = read_config(buildout.overrides.content)
    assert set([
        buildout.source.map('bar'),
        buildout.source.map('foo'),
    ]).issubset(config.get('buildout', 'develop +').split())


def test_develop_paths_in_overrides_have_defined_order(buildout):
    config = read_config(buildout.overrides.content)
    develop_paths = config.get('buildout', 'develop +').split()
    assert develop_paths == sorted(develop_paths)


def test_dist_versions_are_unpinned_in_overrides(buildout):
    config = read_config(buildout.overrides.content)
    assert config.get('versions', 'foo') == ''
    assert config.get('versions', 'bar') == ''


def test_versions_of_setuptools_and_buildout_are_pinned_explicitly(buildout):
    config = read_config(buildout.overrides.content)
    assert config.get('versions', 'setuptools') == str(buildout.setuptools)
    assert config.get('versions', 'zc.buildout') == str(buildout.version)


def test_version_pins_in_overrides_have_defined_order(buildout):
    config = read_config(buildout.overrides.content)
    pins = config.items('versions')
    assert pins == sorted(pins)


def test_shared_egg_dir_is_created_for_service_user(buildout):
    config = read_config(buildout.overrides.content)
    eggs_dir = config.get('buildout', 'eggs-directory')
    assert eggs_dir == buildout.map('~/' + eggs_dir.split('/')[-1])
    assert any(component.path == eggs_dir
               for component in buildout.sub_components
               if isinstance(component, Directory))


root  # XXX satisfy pyflakes
