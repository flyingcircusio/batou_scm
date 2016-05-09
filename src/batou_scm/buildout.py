from batou import UpdateNeeded, SilentConfigurationError
from batou.lib.buildout import Buildout
from batou.lib.file import Directory, File
import pkg_resources


class Buildout(Buildout):

    python = '2.7'
    version = '2.5.0'
    setuptools = '20.7'

    eggs_directory = '~/.batou-shared-eggs'
    versionpins = None

    def configure(self):
        try:
            self.source = self.require_one('source', self.host)
        except (KeyError, SilentConfigurationError):
            # BBB KeyError for batou < 1.1
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


class BuildoutWithVersionPins(Buildout):
    """Buildout which expects a version attribute on the source component.

    It has to be a directory containing a file named `versions.cfg`.
    """

    def configure(self):
        source = self.require_one('source', self.host)
        self.versionpins = source.versions

        # XXX We should depend on all clones we are using in the buildout.cfg,
        # not just the versionpins.
        self.additional_config += (self.versionpins, )

        super(BuildoutWithVersionPins, self).configure()

    def verify(self):
        super(BuildoutWithVersionPins, self).verify()
        # XXX Only checking has_changes won't detect advanced SCM operations
        # like updating to an older revision, but as an 80-20 solution it's
        # quite good enough.
        if (self.versionpins.has_changes
                or self.versionpins.has_outgoing_changesets):
            raise UpdateNeeded()
