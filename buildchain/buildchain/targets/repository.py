# coding: utf-8


"""Provides software repository construction.

A repository is either built from an existing repository (e.g. epel) or build
from locally built packages (e.g. scality).

Note that, for now, we only generate CentOS 7 repository for x86_64
architecture.

Overview:

CASE 1: existing repository

┌────────────┐
│ build_repo │
└────────────┘

CASE 2: local repository

                                 ┌───────────┐
                           ╱────>│build:rpm1 │──────>│
                          ╱      └───────────┘       │
┌─────┐     ┌────────────┐       ┌───────────┐       │       ┌────────────────┐
│mkdir│────>│ build RPMs │──────>│build:rpm2 │──────>│──────>│build repository│
└─────┘     └────────────┘       └───────────┘       │       └────────────────┘
                          ╲      ┌───────────┐       │
                           ╲────>│build:rpm3 │──────>│
                                 └───────────┘
"""

import abc
import operator
from pathlib import Path
from typing import Any, List, Optional, Sequence

from buildchain import config
from buildchain import coreutils
from buildchain import constants
from buildchain import types
from buildchain import utils
from buildchain import docker_command

from . import base
from . import image
from . import package
from . import directory


MKDIR_ROOT_TASK_NAME = 'mkdir_repo_root'
MKDIR_ARCH_TASK_NAME = 'mkdir_repo_arch'


class Repository(base.CompositeTarget):
    """Base class to build a repository of software packages."""

    def __init__(
        self,
        basename: str,
        name: str,
        builder: image.ContainerImage,
        repo_root: Path,
        packages: Optional[Sequence[package.Package]]=None,
        **kwargs: Any
    ):
        """Initialize the repository.

        Arguments:
            basename: basename for the sub-tasks
            name:     repository name
            packages: list of locally built packages
            builder:  docker image used to build the package

        Keyword Arguments:
            They are passed to `Target` init method.
        """
        self._name = name
        self._builder = builder
        self._packages = packages or []
        self._repo_root = repo_root
        super().__init__(
            basename='{base}:{name}'.format(base=basename, name=self.name),
            **kwargs
        )

    name     = property(operator.attrgetter('_name'))
    builder  = property(operator.attrgetter('_builder'))
    packages = property(operator.attrgetter('_packages'))

    @abc.abstractproperty
    def fullname(self) -> str:
        """Repository full name."""

    @property
    def rootdir(self) -> Path:
        """Repository root directory."""
        return self._repo_root/self.fullname

    @property
    def execution_plan(self) -> List[types.TaskDict]:
        tasks = [self.build_repo()]
        if self._packages:
            tasks.extend(self.build_packages())
        return tasks

    @abc.abstractmethod
    def build_repo(self) -> types.TaskDict:
        """Build the repository."""

    @abc.abstractmethod
    def build_packages(self) -> List[types.TaskDict]:
        """Build the packages for the repository."""

    def _mkdir_repo_root(self) -> types.TaskDict:
        """Create the root directory for the repository."""
        task = self.basic_task
        mkdir = directory.Mkdir(directory=self.rootdir).task
        task.update({
            'name': MKDIR_ROOT_TASK_NAME,
            'doc': 'Create root directory for the {} repository.'.format(
                self.name
            ),
            'title': mkdir['title'],
            'actions': mkdir['actions'],
            'uptodate': [True],
            'targets': mkdir['targets'],
        })
        return task


class RPMRepository(Repository):
    """A software repository for CentOS 7 x86_64."""

    SUFFIX = 'el7'
    ARCH   = 'x86_64'

    def __init__(
        self,
        basename: str,
        name: str,
        builder: image.ContainerImage,
        packages: Optional[Sequence[package.RPMPackage]]=None,
        **kwargs: Any
    ):
        super ().__init__(
            basename, name, builder, constants.REPO_RPM_ROOT, packages,
            **kwargs
        )

    @property
    def fullname(self) -> str:
        """Repository full name."""
        return '{project}-{repo}-{suffix}'.format(
            project=config.PROJECT_NAME.lower(),
            repo=self.name, suffix=self.SUFFIX
        )

    @property
    def repodata(self) -> Path:
        """Repository metadata directory."""
        return self.rootdir/'repodata'

    def build_repo(self) -> types.TaskDict:
        """Build the repository."""
        def clean() -> None:
            """Delete the repository metadata directory and its contents."""
            coreutils.rm_rf(self.repodata)

        mkdir = directory.Mkdir(directory=self.repodata).task
        actions = mkdir['actions']
        actions.append(self._buildrepo_action())
        targets = [self.repodata/'repomd.xml']
        targets.extend(mkdir['targets'])

        task = self.basic_task
        task.update({
            'name': 'build_repodata',
            'actions': actions,
            'doc': 'Build the {} repository metadata.'.format(self.name),
            'title': utils.title_with_target1('BUILD RPM REPO'),
            'targets': targets,
            'uptodate': [True],
            'clean': [clean],
            # Prevent Docker from polluting our output.
            'verbosity': 0,
        })
        if self.packages:
            task['task_dep'].append('{base}:{name}'.format(
                base=self.basename, name=MKDIR_ROOT_TASK_NAME
            ))
            task['file_dep'].extend([
                self.get_rpm_path(pkg) for pkg in self.packages
            ])
        return task

    def build_packages(self) -> List[types.TaskDict]:
        """Build the RPMs from SRPMs."""
        tasks = [self._mkdir_repo_root(), self._mkdir_repo_arch()]
        for pkg in self.packages:
            rpm = self.get_rpm_path(pkg)
            env = {
                'RPMS': '{arch}/{rpm}'.format(arch=self.ARCH, rpm=rpm.name),
                'SRPM': pkg.srpm.name,
            }

            buildrpm_callable = docker_command.DockerRun(
                command=['/entrypoint.sh', 'buildrpm'],
                builder=self.builder,
                environment=env,
                mounts=self._get_buildrpm_mounts(pkg.srpm, rpm.parent),
                tmpfs={'/home/build': '', '/var/tmp': ''},
                run_config=docker_command.RPM_BASE_CONFIG
            )

            task = self.basic_task
            task.update({
                'name': 'build_rpm:{}'.format(pkg.name),
                'actions': [buildrpm_callable],
                'doc': 'Build {pkg} RPM for the {repo} repository.'.format(
                    pkg=pkg.name, repo=self.name
                ),
                'title': utils.title_with_target1('BUILD RPM'),
                'targets': [self.get_rpm_path(pkg)],
                # Prevent Docker from polluting our output.
                'verbosity': 0,
            })
            task['file_dep'].append(pkg.srpm)
            task['task_dep'].append('{base}:{name}'.format(
                base=self.basename, name=MKDIR_ARCH_TASK_NAME,
            ))
            task['task_dep'].append(
                '_build_builder:{}'.format(self.builder.name)
            )
            tasks.append(task)
        return tasks

    def _mkdir_repo_arch(self) -> types.TaskDict:
        """Create the CPU architecture directory for the repository."""
        task = self.basic_task
        mkdir = directory.Mkdir(directory=self.rootdir/self.ARCH).task
        task.update({
            'name': MKDIR_ARCH_TASK_NAME,
            'doc': 'Create arch directory for the {} repository.'.format(
                self.name
            ),
            'title': mkdir['title'],
            'actions': mkdir['actions'],
            'uptodate': [True],
            'targets': mkdir['targets'],
        })
        task['task_dep'].append('{base}:{name}'.format(
            base=self.basename, name=MKDIR_ROOT_TASK_NAME
        ))
        return task

    def get_rpm_path(self, pkg: package.RPMPackage) -> Path:
        """Return the path of the RPM of a given package."""
        filename = pkg.srpm.name.replace(
            '.src.rpm', '.{}.rpm'.format(self.ARCH)
        )
        return self.rootdir/self.ARCH/filename

    @staticmethod
    def _get_buildrpm_mounts(
        srpm_path: Path, rpm_dir: Path
    ) -> List[types.Mount]:
        """Return the list of container mounts required by `buildrpm`."""
        mounts = [
            # SRPM directory.
            utils.bind_ro_mount(
                source=srpm_path,
                target=Path('/rpmbuild/SRPMS', srpm_path.name)
            ),
            # RPM directory.
            utils.bind_mount(
                source=rpm_dir,
                target=Path('/rpmbuild/RPMS'),
            ),
            # rpmlint configuration file
            docker_command.RPMLINTRC_MOUNT
        ]

        return mounts

    def _buildrepo_action(self) -> types.Action:
        """Return the command to run `buildrepo` inside a container."""
        mounts = [
            utils.bind_ro_mount(
                source=self.rootdir, target=Path('/repository')
            ),
            utils.bind_mount(
                source=self.repodata, target=Path('/repository/repodata')
            )
        ]
        buildrepo_callable = docker_command.DockerRun(
            command=['/entrypoint.sh', 'buildrepo'],
            builder=self.builder,
            mounts=mounts,
            read_only=True,
            run_config=docker_command.RPM_BASE_CONFIG
        )

        return buildrepo_callable


class DEBRepository(Repository):
    """A software repository for Debian."""

    def __init__(
        self,
        basename: str,
        name: str,
        builder: image.ContainerImage,
        **kwargs: Any
    ):
        super ().__init__(
            basename, name, builder, constants.REPO_DEB_ROOT,
            **kwargs
        )
        task = self.basic_task
        task['task_dep'].append('_download_deb_packages')


    @property
    def fullname(self) -> str:
        """Repository full name."""
        return '{project}-{repo}'.format(
            project=config.PROJECT_NAME.lower(),
            repo=self.name,
        )

    @property
    def pkgdir(self) -> Path:
        """Repository where to download the packages."""
        if self.packages:
            # Built packages are not under a sub-directory.
            return constants.PKG_DEB_ROOT
        return constants.PKG_DEB_ROOT/self.fullname

    def build_packages(self) -> List[types.TaskDict]:
        # Nothing to do: packages are already built.
        return []

    def build_repo(self) -> types.TaskDict:
        def clean() -> None:
            """Delete the repository directory and its contents."""
            coreutils.rm_rf(self.rootdir)

        mkdir = self._mkdir_repo_root()
        actions = mkdir['actions']
        actions.append(self._buildrepo_action())
        targets = [Path(self.rootdir, 'dists/bionic',
                        self.fullname, 'binary-amd64/Packages')]
        targets.extend(mkdir['targets'])

        task = self.basic_task
        task.update({
            'name': 'build_repo',
            'actions': actions,
            'doc': 'Build the {} repository.'.format(self.name),
            'title': utils.title_with_target1('BUILD DEB REPO'),
            'targets': targets,
            'uptodate': [True],
            'clean': [clean],
        })
        for pkg in self.packages:
            task['file_dep'].append(pkg.deb)
        return task

    def _buildrepo_action(self) -> types.Action:
        """Return the command to run `reprepro` inside a container."""
        mounts = [
            utils.bind_ro_mount(
                source=constants.ROOT/'packages'/'debian'/'distributions',
                target=Path('/distributions')
            ),
            utils.bind_ro_mount(source=self.pkgdir, target=Path('/packages')),
            utils.bind_mount(source=self.rootdir, target=Path('/repository'))
        ]
        buildrepo_callable = docker_command.DockerRun(
            command=['/entrypoint.sh', 'buildrepo', self.fullname],
            builder=self.builder,
            mounts=mounts,
            read_only=True,
            run_config=docker_command.DEB_BASE_CONFIG
        )
        return buildrepo_callable
