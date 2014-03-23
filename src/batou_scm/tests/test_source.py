from batou.conftest import root
from batou.lib.mercurial import Clone
from batou_scm.source import Source
import pytest


@pytest.fixture
def source(root):
    source = Source(
        dist_sources=repr([
            'https://example.com/foo',
            'https://example.com/bar branch=BAR',
        ]),
        sources=repr([
            'https://example.com/baz revision=BAZ',
        ]))
    root.component += source
    root.component.configure()
    return source


def test_all_clones_are_configured_as_subcomponents(source):
    clones = [s for s in source.sub_components if isinstance(s, Clone)]
    assert set(clones) == set(source.clones.values())
    assert set(clone.url for clone in clones) == set([
        'https://example.com/foo',
        'https://example.com/bar',
        'https://example.com/baz'])


def test_all_targets_are_derived_from_clone_urls(source):
    assert {clone.url: clone.target for clone in source.clones.values()} == {
        'https://example.com/foo': source.map('foo'),
        'https://example.com/bar': source.map('bar'),
        'https://example.com/baz': source.map('baz')}


def test_distributions_are_collected_separately(source):
    assert {
        clone.url: clone.target for clone in source.distributions.values()
    } == {
        'https://example.com/foo': source.map('foo'),
        'https://example.com/bar': source.map('bar'),
    }


def test_branches_are_read_from_parameters(source):
    assert source.clones['foo'].branch == 'default'
    assert source.clones['bar'].branch == 'BAR'
    assert source.clones['baz'].branch == 'default'


def test_revisions_are_read_from_parameters(source):
    assert source.clones['foo'].revision is None
    assert source.clones['bar'].revision is None
    assert source.clones['baz'].revision == 'BAZ'


root  # XXX satisfy pyflakes
