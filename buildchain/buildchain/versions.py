# coding: utf-8


"""Authoritative listing of image and package versions used in the project.

This module MUST be kept valid in a standalone context, since it is intended
for use in tests and documentation as well.
"""
import operator

from collections import namedtuple
from pathlib import Path
from typing import cast, Dict, Optional, Tuple


Image = namedtuple('Image', ('name', 'version', 'digest'))

# Project-wide versions {{{

CALICO_VERSION     : str = '3.8.2'
K8S_VERSION        : str = '1.11.10'
KEEPALIVED_VERSION : str = '1.3.5-16.el7'
SALT_VERSION       : str = '3000.3'

def load_version_information() -> None:
    """Load version information from `VERSION`."""
    to_update = {
        'VERSION_MAJOR', 'VERSION_MINOR', 'VERSION_PATCH', 'VERSION_SUFFIX'
    }
    with VERSION_FILE.open('r', encoding='utf-8') as fp:
        for line in fp:
            name, _, value = line.strip().partition('=')
            # Don't overwrite random variables by trusting an external file.
            var = name.strip()
            if var in to_update:
                globals()[var] = value.strip()


VERSION_FILE = (Path(__file__)/'../../../VERSION').resolve()

# Metalk8s version.
# (Those declarations are not mandatory, but they help pylint and mypy).
VERSION_MAJOR  : str
VERSION_MINOR  : str
VERSION_PATCH  : str
VERSION_SUFFIX : str

load_version_information()

SHORT_VERSION : str = '{}.{}'.format(VERSION_MAJOR, VERSION_MINOR)
VERSION : str = '{}.{}{}'.format(SHORT_VERSION, VERSION_PATCH, VERSION_SUFFIX)


# }}}
# Container images {{{

CENTOS_BASE_IMAGE : str = 'docker.io/centos'
CENTOS_BASE_IMAGE_SHA256 : str = \
    '6ae4cddb2b37f889afd576a17a5286b311dcbf10a904409670827f6f9b50065e'

NGINX_IMAGE_VERSION  : str = '1.15.8'
NODEJS_IMAGE_VERSION : str = '10.16.0'

# Current build IDs, to be augmented whenever we rebuild the corresponding
# image, e.g. because the `Dockerfile` is changed, or one of the dependencies
# installed in the image needs to be updated.
# This should be reset to 1 when the service exposed by the container changes
# version.
SALT_MASTER_BUILD_ID = 1
KEEPALIVED_BUILD_ID  = 1


def _version_prefix(version: str, prefix: str = 'v') -> str:
    return "{}{}".format(prefix, version)


# Digests are quite a mouthful, so:
# pylint:disable=line-too-long
CONTAINER_IMAGES : Tuple[Image, ...] = (
    # Remote images
    Image(
        name='addon-resizer',
        version='1.8.3',
        digest='sha256:07353f7b26327f0d933515a22b1de587b040d3d85c464ea299c1b9f242529326',
    ),
    Image(
        name='alertmanager',
        version='v0.17.0',
        digest='sha256:3db6eccdbf4bdaea3407b7a9e6a41fc50abcf272a1356227260948e73414ec09',
    ),
    Image(
        name='calico-node',
        version=_version_prefix(CALICO_VERSION),
        digest='sha256:6679ccc9f19dba3eb084db991c788dc9661ad3b5d5bafaa3379644229dca6b05',
    ),
    Image(
        name='calico-kube-controllers',
        version=_version_prefix(CALICO_VERSION),
        digest='sha256:cf461efd25ee74d1855e1ee26db98fe87de00293f7d039212adb03c91fececcd',
    ),
    Image(
        name='configmap-reload',
        version='v0.0.1',
        digest='sha256:e2fd60ff0ae4500a75b80ebaa30e0e7deba9ad107833e8ca53f0047c42c5a057',
    ),
    Image(
        name='coredns',
        version='1.3.1',
        digest='sha256:02382353821b12c21b062c59184e227e001079bb13ebd01f9d3270ba0fcbf1e4',
    ),
    Image(
        name='etcd',
        version='3.2.18',
        digest='sha256:b960569ade5f37205a033dcdc3191fe99dc95b15c6795a6282859070ec2c6124',
    ),
    Image(
        name='grafana',
        version='6.3.5',
        digest='sha256:f398faf159712dbfddada80679f1411b1baa6fca3ee08317d785c41a2972124a',
    ),
    Image(
        name='k8s-sidecar',
        version='0.1.20',
        digest='sha256:af151f677a63cdfcdfc18a4e3043520ec506d5e116692e5190f6f765dca42a52',
    ),
    Image(
        name='kube-apiserver',
        version=_version_prefix(K8S_VERSION),
        digest='sha256:a6733a3ec08e4a84d5d1492c0fa2833b6d067ea78e37c87fcffc47bd1ab4ed9c',
    ),
    Image(
        name='kube-controller-manager',
        version=_version_prefix(K8S_VERSION),
        digest='sha256:f5ddb81466e7467dacc8b6498bdd117ab77fb2fdb0b333c4ebe3e95e5493a661',
    ),
    Image(
        name='kube-proxy',
        version=_version_prefix(K8S_VERSION),
        digest='sha256:fd6c29a779b3e30ad4072a1c77aef49f20bd3ea6cbd290c6f47be28ef333bb69',
    ),
    Image(
        name='kube-rbac-proxy',
        version='v0.3.1',
        digest='sha256:a578315f24e6fd01a65e187e4d1979678598a7d800d039ee5cfe4e11b0b1788d',
    ),
    Image(
        name='kube-scheduler',
        version=_version_prefix(K8S_VERSION),
        digest='sha256:119fcd453469b7a3cc644ea7cda992371c5b746ef705dd88d7a8bfefae48b3be',
    ),
    Image(
        name='kube-state-metrics',
        version='v1.7.2',
        digest='sha256:99a3e3297e281fec09fe850d6d4bccf4d9fd58ff62a5b37764d8a8bd1e79bd14',
    ),
    Image(
        name='nginx',
        version=NGINX_IMAGE_VERSION,
        digest='sha256:f09fe80eb0e75e97b04b9dfb065ac3fda37a8fac0161f42fca1e6fe4d0977c80',
    ),
    Image(
        name='nginx-ingress-controller',
        version='0.25.0',
        digest='sha256:464db4880861bd9d1e74e67a4a9c975a6e74c1e9968776d8d4cc73492a56dfa5',
    ),
    Image(
        name='nginx-ingress-defaultbackend-amd64',
        version='1.5',
        digest='sha256:4dc5e07c8ca4e23bddb3153737d7b8c556e5fb2f29c4558b7cd6e6df99c512c7',
    ),
    Image(
        name='node-exporter',
        version='v0.18.0',
        digest='sha256:b2dd31b0d23fda63588674e40fd8d05010d07c5d4ac37163fc596ba9065ce38d',
    ),
    Image(
        name='pause',
        version='3.1',
        digest='sha256:da86e6ba6ca197bf6bc5e9d900febd906b133eaa4750e6bed647b0fbe50ed43e',
    ),
    Image(
        name='prometheus',
        version='v2.12.0',
        digest='sha256:cd93b8711bb92eb9c437d74217311519e0a93bc55779aa664325dc83cd13cb3',
    ),
    Image(
        name='prometheus-config-reloader',
        version='v0.32.0',
        digest='sha256:f1e57817dcfdb2c76e8a154b39180c6c8f3f16b990fe9cc41bee34cca0784a64',
    ),
    Image(
        name='prometheus-operator',
        version='v0.32.0',
        digest='sha256:ed3ec0597c2d5b7102a7f62c661a23d8e4b34d910693fc23fd40bfb1d9404dcf',
    ),
    # Local images
    Image(
        name='keepalived',
        version='{version}-{build_id}'.format(
            version=KEEPALIVED_VERSION, build_id=KEEPALIVED_BUILD_ID
        ),
        digest=None,
    ),
    Image(
        name='metalk8s-utils',
        version=VERSION,
        digest=None,
    ),
    Image(
        name='salt-master',
        version='{version}-{build_id}'.format(
            version=SALT_VERSION, build_id=SALT_MASTER_BUILD_ID
        ),
        digest=None,
    ),
)

CONTAINER_IMAGES_MAP = {image.name: image for image in CONTAINER_IMAGES}

# }}}

# Packages {{{

class PackageVersion:
    """A package's authoritative version data.

    This class contains version information for a named package, and
    provides helper methods for formatting version/release data as well
    as version-enriched package name, for all supported OS families.
    """

    def __init__(
        self,
        name: str,
        version: Optional[str] = None,
        release: Optional[str] = None,
        override: Optional[str] = None
    ):
        """Initializes a package version.

        Arguments:
            name: the name of the package
            version: the version of the package
            release: the release of the package
        """
        self._name     = name
        self._version  = version
        self._release  = release
        self._override = override

    name = property(operator.attrgetter('_name'))
    version = property(operator.attrgetter('_version'))
    release = property(operator.attrgetter('_release'))
    override = property(operator.attrgetter('_override'))

    @property
    def full_version(self) -> Optional[str]:
        """The full package version string."""
        full_version = None
        if self.version:
            full_version = self.version
            if self.release:
                full_version = '{}-{}'.format(self.version, self.release)
        return full_version

    @property
    def rpm_full_name(self) -> str:
        """The package's full name in RPM conventions."""
        if self.full_version:
            return '{}-{}'.format(self.name, self.full_version)
        return cast(str, self.name)



# The authoritative list of packages required.
#
# Common packages are packages for which we need not care about OS-specific
# divergences.
#
# In this case, either:
#   * the _latest_ version is good enough, and will be the one
#     selected by the package managers (so far: apt and yum).
#   * we have strict version requirements that span OS families, and the
#     version schemes _and_ package names do not diverge
#
# Strict version requirements are notably:
#   * kubelet and kubectl which _make_ the K8s version of the cluster
#   * salt-minion which _makes_ the Salt version of the cluster
#
# These common packages may be overridden by OS-specific packages if package
# names or version conventions diverge.
#
# Packages that we build ourselves require a version and release as part of
# their build process.
PACKAGE_LIST: Dict[str, Tuple[PackageVersion, ...]] = {
    'common': (
        # Pinned packages
        PackageVersion(name='kubectl', version=K8S_VERSION),
        PackageVersion(name='kubelet', version=K8S_VERSION),
        # Latest packages
        PackageVersion(name='containerd'),
        PackageVersion(name='coreutils'),
        PackageVersion(name='cri-tools'),
        PackageVersion(name='e2fsprogs'),
        PackageVersion(name='ebtables'),
        PackageVersion(name='ethtool'),
        PackageVersion(name='genisoimage'),
        PackageVersion(name='iproute'),
        PackageVersion(name='iptables'),
        # NOTE: kubelet require `kubernetes-cni = 0.7.5`
        PackageVersion(name='kubernetes-cni', version='0.7.5'),
        PackageVersion(name='m2crypto'),
        PackageVersion(name='runc'),
        PackageVersion(name='salt-minion', version=SALT_VERSION),
        PackageVersion(name='socat'),
        PackageVersion(name='sos'),  # TODO download built package dependencies
        PackageVersion(name='util-linux'),
        PackageVersion(name='xfsprogs'),
    ),
    'redhat': (
        PackageVersion(
            name='calico-cni-plugin',
            version=CALICO_VERSION,
            release='1.el7'
        ),
        PackageVersion(name='container-selinux'),  # TODO #1710
        PackageVersion(
            name='metalk8s-sosreport',
            version=SHORT_VERSION,
            release='1.el7'
        ),
        PackageVersion(name='yum-plugin-versionlock'),
    ),
}


def _list_pkgs_for_os_family(os_family: str) -> Tuple[PackageVersion, ...]:
    """List downloaded packages for a given OS family.

    Arguments:
        os_family: OS_family for which to list packages
    """
    common_pkgs = PACKAGE_LIST['common']
    os_family_pkgs = PACKAGE_LIST.get(os_family)

    if os_family_pkgs is None:
        raise Exception('No packages for OS family: {}'.format(os_family))

    os_override_names = [
        pkg.override for pkg in os_family_pkgs
        if pkg.override is not None
    ]

    overridden = filter(
        lambda item: item.name not in os_override_names,
        common_pkgs
    )

    return tuple(overridden) + os_family_pkgs


PACKAGES = _list_pkgs_for_os_family('redhat')

PACKAGES_MAP = {pkg.name: pkg for pkg in PACKAGES}

# }}}
