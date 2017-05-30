from batou import UpdateNeeded
from batou.conftest import root
from batou.lib.file import Directory
from batou_scm.buildout import Buildout, BuildoutWithVersionPins
from batou_scm.source import Source
import ConfigParser
import StringIO
import mock
import pytest


@pytest.fixture
def buildout(root):
    source = Source(
        dist_sources=repr([
            'hg+https://example.com/foo',
            'hg+https://example.com/bar',
        ]))
    root.component += source
    root.component += Buildout()
    root.component.configure()
    return root.component._


@pytest.fixture(scope='function')
def buildout_with_version_pins(root):
    source = Source(
        dist_sources=repr([
            'hg+https://example.com/foo',
            'hg+https://example.com/bar',
        ]),
        sources=repr(['hg+https://example.com/ver target=versions']))
    root.component += source
    source.versions = source.clones['versions']
    root.component += BuildoutWithVersionPins()
    root.component.configure()
    return root.component._


def read_config(content):
    config = ConfigParser.ConfigParser()
    config.readfp(StringIO.StringIO(content))
    return config


def test_buildout_doesnt_need_source_to_be_configured(root):
    root.component += Buildout()
    root.component.configure()
    assert '.batou-shared-eggs' in root.component._.overrides.content
    with pytest.raises(UpdateNeeded):
        root.component._.verify()


def test_dist_paths_are_listed_as_develop_paths_in_overrides(buildout):
    config = read_config(buildout.overrides.content)
    assert set([
        buildout.source.map('bar'),
        buildout.source.map('foo'),
    ]).issubset(config.get('buildout', 'develop +').split())


def test_no_dist_sources_configured_does_not_break(root):
    source = Source()
    root.component += source
    root.component += Buildout()
    root.component.configure()
    buildout = root.component._
    assert 'develop +=' not in buildout.overrides.content
    assert buildout.source is not None


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


def test_verify_checks_source(buildout):
    with mock.patch('batou.lib.buildout.Buildout.verify'):
        with mock.patch('batou.lib.mercurial.Clone.has_changes') \
                as has_changes:
            has_changes.return_value = False
            buildout.source.assert_no_subcomponent_changes = mock.Mock()
            buildout.verify()
            assert buildout.source.assert_no_subcomponent_changes.called
            assert has_changes.called


def test_verify_result_is_cached(buildout):
    with mock.patch('batou.lib.buildout.Buildout.verify'):
        with mock.patch('batou.lib.mercurial.Clone.has_changes'):
            with mock.patch.object(
                    buildout.source, 'assert_no_subcomponent_changes') as ansc:
                ansc.side_effect = UpdateNeeded
                with pytest.raises(UpdateNeeded):
                    buildout.verify()
                with pytest.raises(UpdateNeeded):
                    buildout.verify()
                assert 1 == ansc.call_count


def test_buildout__BuildoutWithVersionPins__verify__1(
        buildout_with_version_pins):
    """`verify()` requests update on changed versions."""
    buildout = buildout_with_version_pins
    with mock.patch('batou.lib.mercurial.Clone.has_changes') \
            as has_changes:
        has_changes.return_value = True
        with pytest.raises(UpdateNeeded):
            buildout.verify()


def test_buildout__BuildoutWithVersionPins__verify__2(
        buildout_with_version_pins):
    """`verify()` requests update on outgoing changes in versions."""
    buildout = buildout_with_version_pins
    with mock.patch('batou.lib.mercurial.Clone.has_outgoing_changesets') \
            as has_outgoing_changesets, \
            mock.patch('batou.lib.mercurial.Clone.has_changes') \
            as has_changes:
        has_changes.return_value = False
        has_outgoing_changesets.return_value = True
        with pytest.raises(UpdateNeeded):
            buildout.verify()


root  # XXX satisfy pyflakes
