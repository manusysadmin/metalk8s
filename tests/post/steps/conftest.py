# -*- coding: utf-8 -*-
import pytest
from pytest_bdd import (
    given,
    then,
    when,
    parsers,
)
import yaml

from tests import kube_utils


# Pytest fixtures
@pytest.fixture(scope="module")
def kubeconfig_data(request, host):
    """Fixture to generate a kubeconfig file for remote usage."""
    with host.sudo():
        kubeconfig_file = host.file('/etc/kubernetes/admin.conf')
        if not kubeconfig_file.exists:
            pytest.skip(
                "Must be run on bootstrap node, or have an existing file at "
                "/etc/kubernetes/admin.conf"
            )
        data = yaml.safe_load(kubeconfig_file.content_string)

    kube_cluster_section = next(
        cluster_info["cluster"] for cluster_info in data["clusters"]
        if cluster_info["name"] == "kubernetes"
    )

    # FIXME: this should not be necessary, we should run the tests from within
    #        the control-plane network
    bootstrap_ip = request.config.getoption("--bootstrap-ip")
    if bootstrap_ip is not None:
        kube_cluster_section["server"] = "https://{}:6443".format(bootstrap_ip)

    if request.config.getoption("--skip-tls-verify"):
        kube_cluster_section["insecure-skip-tls-verify"] = True

    return data


@pytest.fixture
def kubeconfig(kubeconfig_data, tmp_path):
    kubeconfig_path = tmp_path / "admin.conf"
    kubeconfig_path.write_text(yaml.dump(kubeconfig_data), encoding='utf-8')
    return str(kubeconfig_path)  # Need Python 3.6 to open() a Path object


@pytest.fixture
def version(request, host):
    iso_root = request.config.getoption("--iso-root")
    product_path = iso_root / "product.txt"
    with host.sudo():
        return host.check_output(
            'source %s && echo $SHORT_VERSION', str(product_path)
        )


def _verify_kubeapi_service(host):
    """Verify that the kubeapi service answer"""
    with host.sudo():
        cmd = "kubectl --kubeconfig=/etc/kubernetes/admin.conf cluster-info"
        retcode = host.run(cmd).rc
        assert retcode == 0


def _run_bootstrap(request, host):
    # FIXME: this can only run on the bootstrap node, we'd need to skip such
    #        test if the host fixture is not adapted
    iso_root = request.config.getoption("--iso-root")
    cmd = str(iso_root / "bootstrap.sh")
    with host.sudo():
        res = host.run(cmd)
        assert res.rc == 0, res.stdout


# Pytest-bdd steps

# Given
@given('bootstrap was run once')
def run_bootstrap(request, host):
    _run_bootstrap(request, host)


@given("the Kubernetes API is available")
def check_service(host):
    _verify_kubeapi_service(host)


@given(parsers.parse("pods with label '{label}' are '{state}'"))
def check_pod_state(host, label, state):
    pods = kube_utils.get_pods(
        host, label, namespace="kube-system", status_phase="Running",
    )

    assert len(pods) > 0, "No {} pod with label '{}' found".format(
        state.lower(), label
    )


# When
@when('we run bootstrap a second time')
def rerun_bootstrap(request, host):
    _run_bootstrap(request, host)


# Then
@then("the Kubernetes API is available")
def verify_kubeapi_service(host):
    _verify_kubeapi_service(host)
