from batou.lib.buildout import Buildout
from batou.lib.file import Directory, File
import pkg_resources


class Buildout(Buildout):

    python = '2.7'
    version = '2.2.1'
    setuptools = '1.3'

    def configure(self):
        self.source = self.require_one('source', self.host)

        self.dist_names, distributions = zip(
            *sorted(self.source.distributions.items()))
        self.dist_paths = [clone.target for clone in distributions]
        self.additional_config += distributions

        # A directory for eggs shared by buildouts within the deployment is
        # created for the service user. Assuming that a user cannot have
        # multiple non-sandboxed deployments and that development deployments
        # are sandboxed, eggs are never shared across deployments or users.
        self.eggs_directory = Directory('~/.batou-shared-eggs')
        self += self.eggs_directory

        self.overrides = File(
            'buildout_overrides.cfg',
            source=pkg_resources.resource_filename(
                'batou_scm', 'resources/buildout_overrides.cfg'))
        self += self.overrides

        super(Buildout, self).configure()

    @property
    def versions(self):
        result = {'setuptools': self.setuptools, 'zc.buildout': self.version}
        result.update({name: '' for name in self.dist_names})
        return sorted(result.items())