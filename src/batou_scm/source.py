from batou.component import Component
from batou.lib.file import File, Content
import ast
import batou.lib.git
import batou.lib.mercurial
import collections
import os.path
import pkg_resources
import urlparse


class Source(Component):

    dist_sources = '[]'
    sources = '[]'

    hg_hostfingerprints = {
        'bitbucket.org':
        'SHA256:32:12:90:9A:70:64:82:1C:5B:52:CC:C3:0A:D0:79:DB:E1:A8:62:1B:9A:9A:4C:F4:72:40:1C:A7:3A:D3:0A:8C',
    }
    additional_hgrc_content = ''

    vcs_update = 'True'

    def _eval_attr(self, *names):
        for name in names:
            if isinstance(getattr(self, name), basestring):
                setattr(self, name, ast.literal_eval(getattr(self, name)))

    def configure(self):
        self._eval_attr('dist_sources', 'sources', 'vcs_update',
                        'hg_hostfingerprints')

        self.hg_hostfingerprints = collections.OrderedDict(
            x for x in sorted(self.hg_hostfingerprints.items()))

        self.provide('source', self)

        additional_hgrc = os.path.join(self.defdir, 'hgrc')
        if not self.additional_hgrc_content and os.path.exists(
                additional_hgrc):
            self |= Content('additional_hgrc', source=additional_hgrc)
            self.additional_hgrc_content = self._.content

        self.hgrc = File('~/.hgrc', source=pkg_resources.resource_filename(
            'batou_scm', 'resources/hgrc'))
        self += self.hgrc

        self.distributions = dict(
            self.add_clone(url) for url in self.dist_sources)
        self.clones = self.distributions.copy()
        self.clones.update(self.add_clone(url) for url in self.sources)

    VCS = {
        'hg': {
            'component': batou.lib.mercurial.Clone,
            'default-branch': 'default',
        },
        'git': {
            'component': batou.lib.git.Clone,
            'default-branch': 'master',
        },
    }

    def add_clone(self, url):
        parts = urlparse.urlsplit(url)
        vcs, _, scheme = parts.scheme.partition('+')
        if not vcs:
            raise ValueError(
                'Malformed VCS URL %r, need <vcs>+<protocol>://<url>, '
                'e.g. hg+ssh://hg@bitbucket.org/gocept/batou' % url)
        url = urlparse.urlunsplit((scheme,) + parts[1:])

        url, _, parameter_list = url.partition(' ')
        parameters = {}
        parameters['target'] = filter(bool, url.split('/'))[-1]
        parameters.update(x.split('=') for x in parameter_list.split())
        if 'branch' not in parameters and 'revision' not in parameters:
            parameters['branch'] = self.VCS[vcs]['default-branch']

        clone = self.VCS[vcs]['component']
        self += clone(url, vcs_update=self.vcs_update, **parameters)
        return parameters['target'], self._
