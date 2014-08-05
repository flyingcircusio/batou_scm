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
    source.defdir = root.defdir
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
code.gocept.com = 5e:ec:16:18:7a:4a:c1:33:9d:7d:35:42:ff:f4:39:69:3f:8c:66:d6
example.com = fpr2
""")


def test_additional_hgrc_content_is_taken_from_file_if_present(source):
    open(os.path.join(source.defdir, 'hgrc'), 'w').write('foo')
    source.configure()
    assert 'foo' in source.hgrc.content


root  # XXX satisfy pyflakes
