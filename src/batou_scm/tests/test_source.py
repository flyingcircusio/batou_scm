from batou.conftest import root
from batou.lib.mercurial import Clone
from batou_scm.source import Source
import os.path
import pytest


@pytest.fixture
def source(root):
    source = Source(
        dist_sources=repr([
            'hg+https://example.com/foo',
            'hg+https://example.com/bar branch=BAR',
        ]),
        sources=repr([
            'hg+https://example.com/baz revision=BAZ',
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
    assert source.clones['bar'].branch == 'BAR'


def test_branch_is_set_to_default_if_not_given(source):
    assert source.clones['foo'].branch == 'default'


def test_branch_is_not_set_if_revision_given(source):
    assert source.clones['baz'].branch is None


def test_revisions_are_read_from_parameters(source):
    assert source.clones['foo'].revision is None
    assert source.clones['bar'].revision is None
    assert source.clones['baz'].revision == 'BAZ'


def test_hg_hostfingerprints_are_sorted(source):
    source.hg_hostfingerprints['bitbucket.org'] = 'fpr1'
    source.hg_hostfingerprints['example.com'] = 'fpr2'
    source.configure()
    assert source.hgrc.content.startswith("""\
[hostfingerprints]
bitbucket.org = fpr1
code.gocept.com = 61:3f:8d:c9:b5:1f:65:79:68:d2:7d:1b:45:a2:c9:cb:b0:b4:32:de
example.com = fpr2
""")


def test_additional_hgrc_content_is_taken_from_file_if_present(source):
    open(os.path.join(source.defdir, 'hgrc'), 'w').write('foo')
    source.configure()
    assert 'foo' in source.hgrc.content


root  # XXX satisfy pyflakes
