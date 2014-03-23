from batou.component import Component
from batou.lib.file import File
from batou.lib.mercurial import Clone
import ast
import pkg_resources


class Source(Component):

    dist_sources = '[]'
    sources = '[]'

    vcs_update = 'True'

    def _eval_attr(self, *names):
        for name in names:
            if isinstance(getattr(self, name), basestring):
                setattr(self, name, ast.literal_eval(getattr(self, name)))

    def configure(self):
        self._eval_attr('dist_sources', 'sources', 'vcs_update')

        self.provide('source', self)

        self += File('~/.hgrc', source=pkg_resources.resource_filename(
            'batou_scm', 'resources/hgrc'))

        self.distributions = dict(
            self.add_clone(url) for url in self.dist_sources)
        self.clones = self.distributions.copy()
        self.clones.update(self.add_clone(url) for url in self.sources)

    def add_clone(self, url):
        url, _, parameter_list = url.partition(' ')
        parameters = dict(
            target=filter(bool, url.split('/'))[-1],
            branch='default',
        )
        parameters.update(x.split('=') for x in parameter_list.split())
        name = parameters['target']
        self += Clone(url, vcs_update=self.vcs_update, **parameters)
        return name, self._
