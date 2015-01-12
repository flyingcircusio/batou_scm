from batou import UpdateNeeded
from batou.lib.buildout import Buildout
from batou.lib.file import Directory, File
import pkg_resources


class Buildout(Buildout):

    python = '2.7'
    version = '2.2.1'
    setuptools = '1.3'

    eggs_directory = '~/.batou-shared-eggs'

    def configure(self):
        try:
            self.source = self.require_one('source', self.host)
        except KeyError:
            have_dists = False
            self.source = None
        else:
            have_dists = len(self.source.distributions)

        if have_dists:
            self.dist_names, distributions = zip(
                *sorted(self.source.distributions.items()))
            self.dist_paths = [clone.target for clone in distributions]
        else:
            self.dist_names = []
            self.dist_paths = []

        # A directory for eggs shared by buildouts within the deployment is
        # created for the service user. Assuming that a user cannot have
        # multiple non-sandboxed deployments and that development deployments
        # are sandboxed, eggs are never shared across deployments or users.
        self.eggs_directory = Directory(self.eggs_directory)
        self += self.eggs_directory

        self.overrides = File(
            'buildout_overrides.cfg',
            source=pkg_resources.resource_filename(
                'batou_scm', 'resources/buildout_overrides.cfg'))
        self.additional_config += (self.overrides,)

        super(Buildout, self).configure()

    @property
    def versions(self):
        result = {'setuptools': self.setuptools, 'zc.buildout': self.version}
        result.update({name: '' for name in self.dist_names})
        return sorted(result.items())

    __update_needed = None

    def verify(self):
        # We need to re-run buildout if any of the sources has changed.
        # This check incurs network access for each source checkout, so we
        # want to short-cut repeated calls.
        if self.source and self.__update_needed is None:
            try:
                self.source.assert_no_subcomponent_changes()
            except UpdateNeeded:
                self.__update_needed = True
            else:
                self.__update_needed = False
            for clone in self.source.clones.values():
                if clone.has_changes:
                    self.__update_needed = True
        if self.__update_needed:
            raise UpdateNeeded()
        super(Buildout, self).verify()
