# -*- coding: utf-8 -*-
"""
Execution module for handling MetalK8s checks.
"""

import ipaddress
import psutil
import re

from salt.exceptions import CheckError

__virtualname__ = "metalk8s_checks"


def __virtual__():
    return __virtualname__


def node(raises=True, **kwargs):
    """Check if the current Salt-minion match some requirements so that it can
    be used as a MetalK8s node.

    Arguments:
        raises (bool): the method will raise if there is any problem.

    Optional arguments:
        service_cidr (str): the network CIDR for Service Cluster IPs (for
            which to check the presence of a route) - if not given nor set in
            `pillar.networks.service`, this check will be skipped.
    """
    errors = []

    # Run `packages` check
    pkg_ret = __salt__["metalk8s_checks.packages"](raises=False, **kwargs)
    if pkg_ret is not True:
        errors.append(pkg_ret)

    # Run `services` check
    svc_ret = __salt__["metalk8s_checks.services"](raises=False, **kwargs)
    if svc_ret is not True:
        errors.append(svc_ret)

    # Run `route_exists` check for the Service Cluster IPs
    service_cidr = kwargs.pop(
        "service_cidr", __pillar__.get("networks", {}).get("service", None)
    )
    if service_cidr is not None:
        service_route_ret = route_exists(destination=service_cidr, raises=False)
        if service_route_ret is not True:
            errors.append(
                (
                    "Invalid networks:service CIDR - {}. Please make sure to "
                    "have either a default route or a dummy interface and route "
                    "for this range (for details, see "
                    "https://github.com/kubernetes/kubernetes/issues/57534#issuecomment-527653412)."
                ).format(service_route_ret)
            )

    # Compute return of the function
    if errors:
        error_msg = "Node {}: {}".format(__grains__["id"], "\n".join(errors))
        if raises:
            raise CheckError(error_msg)
        return error_msg

    return True


def packages(conflicting_packages=None, raises=True, **kwargs):
    """Check if some conflicting package are installed on the machine,
    return a string (or raise if `raises` is set to `True`) with the list of
    conflicting packages.

    Arguments:
        conflicting_packages (dict): override the list of package that conflict
            with MetalK8s installation.
        raises (bool): the method will raise if there is any conflicting
            package.

    Note: We have some logic in this function, so `conflicting_packages` could
    be:
    - a single string `<package_name>` which is the name of the conflicting
      package (it means we conflict with all versions of this package)
    - a list `[<package_name1>, <package_name2]` with all conflicting package
      names (it means we conflict with all versions of those packages)
    - a dict `{<package1_name>: <package1_versions>, <package2_name>: <package2_versions>}`
      where `package_versions` could be
      - `None` mean we conflicting with all versions of this package
      - A string for a single conflicting version of this package
      - A list of string for multiple conflicting versions of this package
    """
    if conflicting_packages is None:
        conflicting_packages = __salt__["metalk8s.get_from_map"](
            "repo", saltenv=kwargs.get("saltenv")
        )["conflicting_packages"]

    if isinstance(conflicting_packages, str):
        conflicting_packages = {conflicting_packages: None}
    elif isinstance(conflicting_packages, list):
        conflicting_packages = {package: None for package in conflicting_packages}
    errors = []

    installed_packages = __salt__["pkg.list_pkgs"](attr="version")
    for package, version in conflicting_packages.items():
        if isinstance(version, str):
            version = [version]
        if package in installed_packages:
            conflicting_versions = set(
                pkg_info["version"] for pkg_info in installed_packages[package]
            )
            if version:
                conflicting_versions.intersection_update(version)

            if conflicting_versions:
                for ver in sorted(conflicting_versions):
                    errors.append(
                        "Package {}-{} conflicts with MetalK8s installation, "
                        "please remove it.".format(package, ver)
                    )

    error_msg = "\n".join(errors)
    if error_msg and raises:
        raise CheckError(error_msg)

    return error_msg or True


def services(conflicting_services=None, raises=True, **kwargs):
    """Check if some conflicting service are started on the machine,
    return a string (or raise if `raises` is set to `True`) with the list of
    conflicting services.

    Arguments:
        conflicting_services (list): override the list of service that conflict with
            MetalK8s installation.
        raises (bool): the method will raise if there is any conflicting service
            started.

    Note: We have some logic in this function, so `conflicting_services` could be:
    - a single string `<service_name>` which is the name of the conflicting service
    - a list `[<service_name1>, <service_name2>]` with all conflicting service name
    """
    if conflicting_services is None:
        conflicting_services = __salt__["metalk8s.get_from_map"](
            "defaults", saltenv=kwargs.get("saltenv")
        )["conflicting_services"]

    if isinstance(conflicting_services, str):
        conflicting_services = [conflicting_services]
    errors = []

    for service_name in conflicting_services:
        # `service.status`:
        #   True = service started
        #   False = service not available or stopped
        # `service.disabled`:
        #   True = service disabled or not available
        #   False = service not disabled
        if __salt__["service.status"](service_name) or not __salt__["service.disabled"](
            service_name
        ):
            errors.append(
                "Service {} conflicts with MetalK8s installation, "
                "please stop and disable it.".format(service_name)
            )

    error_msg = "\n".join(errors)
    if error_msg and raises:
        raise CheckError(error_msg)

    return error_msg or True


def _listening_process_as_dict(listening_process):
    """Get various listening_process object data and create the expected dict
    to be used by the `ports` function
    """
    if isinstance(listening_process, str) or isinstance(listening_process, int):
        return {listening_process: None}
    if isinstance(listening_process, list):
        return {l_process: None for l_process in listening_process}
    if isinstance(listening_process, dict):
        return listening_process

    raise ValueError(
        "Invalid listening process, expected str, int, list or dict but got {}".format(
            type(listening_process).__name__
        )
    )


def ports(
    listening_process=None,
    raises=True,
    listening_process_per_role=None,
    roles=None,
    **kwargs
):
    """Check if an unexpected process already listening on a port on the machine,
    return a string (or raise if `raises` is set to `True`) with the list of
    unexpected process and port.

    Arguments:
        listening_process (dict): override the list of ports expected to be
            unused (or bind to a MetalK8s process).
        raises (bool): the method will raise if there is any unexpected process
            bind on a MetalK8s port.
        listening_process_per_role (dict): If `listening_process` not provided
            compute it from this dict. Dict matching between listening process
            and roles (default: retrieve using map.jinja)
        roles (list): List of local role for the node (default: retrieve from
            pillar)

    Note: We have some logic in this function, so `listening_process` could
    be:
    - a single string/int `<address>` which is the address to check
      (it means we expect to have no process listening on this address)
    - a list `[<address1>, <address2>]` with all address to check
      (it means we expect to have no process listening on those address)
    - a dict `{<address1>: <processes1>, <address2>: <processes2>}`
      where `processes` could be
      - `None` mean we expect to have no process listening on this address
      - A string for a single process name to listen on this address
        (string could also be a regexp to match process name)
      - A list of process that could listen on this address

    Where `address` could be a full address `<ip>:<port>` or just a `<port>`.
    Note: if `<ip>` is equal to `_control_plane_ip_` or `_workload_plane_ip_` we
    replace this IP with the local expected IP.
    """
    if listening_process is None:
        if listening_process_per_role is None:
            listening_process_per_role = __salt__["metalk8s.get_from_map"](
                "networks", saltenv=kwargs.get("saltenv")
            )["listening_process_per_role"]
        if roles is None:
            roles = __pillar__["metalk8s"]["nodes"][__grains__["id"]]["roles"]

        # Compute full dict of listening process according to local `roles`
        listening_process = {}
        for role in roles:
            listening_process.update(
                _listening_process_as_dict(listening_process_per_role.get(role, {}))
            )
    else:
        listening_process = _listening_process_as_dict(listening_process)

    errors = []

    # Compute current listen connections as
    # `{'<port>': {'<ip>': {'pid': <pid>, 'name': '<name>'}}`
    all_listen_connections = {}
    for sconn in psutil.net_connections("inet"):
        if sconn.status != psutil.CONN_LISTEN:
            continue

        ip, port = sconn.laddr
        # If `<ip>` is `::1` replace with `127.0.0.1` so that we consider only IPv4
        if ip == "::1":
            ip = "127.0.0.1"
        # If `<ip>` is `::` replace with `0.0.0.0` so that we consider only IPv4
        elif ip == "::":
            ip = "0.0.0.0"

        all_listen_connections.setdefault(str(port), {}).update(
            {
                ip: {
                    "pid": sconn.pid,
                    "name": psutil.Process(sconn.pid).name(),
                }
            }
        )

    for address, processes in listening_process.items():
        if isinstance(address, int):
            address = str(address)
        ip = None
        port = address
        if len(address.rsplit(":")) == 2:
            ip, port = address.rsplit(":")

        if ip and ip in ["control_plane_ip", "workload_plane_ip"]:
            ip = __grains__["metalk8s"][ip]

        if not isinstance(processes, list):
            processes = [processes]

        process_on_port = all_listen_connections.get(port)

        failures = []
        # If one of this process is expected one, succeed
        for process in processes:
            error_process = {}
            fail = False
            fail_msg = ""

            # We expect nothing to be listening on this port
            if process is None:
                fail_msg = "Nothing should be listening"

                if process_on_port:
                    # Failure:
                    # - we expect nothing listening on this port
                    # - a process listen on every IPs
                    # - something already listening on the expected IP
                    # NOTE: Normaly if a process listen on `0.0.0.0` we do not
                    # have any other process on this port
                    if not ip:
                        error_process = process_on_port
                        fail = True
                    if "0.0.0.0" in process_on_port:
                        error_process["0.0.0.0"] = process_on_port["0.0.0.0"]
                        fail = True
                    if ip in process_on_port:
                        error_process[ip] = process_on_port[ip]
                        fail = True

            # We expect "<process>" to be listening on this port
            # NOTE: if nothing listening it's a failure
            else:
                fail_msg = "Listening process should match '{}'".format(process)
                # Failure:
                # - nothing listening on this ip:port
                # - nothing listening on the expected IP
                # - something not expected already listening
                if (
                    not process_on_port
                    or ip
                    and "0.0.0.0" not in process_on_port
                    and ip not in process_on_port
                ):
                    fail = True
                elif "0.0.0.0" in process_on_port and not re.match(
                    process, process_on_port["0.0.0.0"]["name"]
                ):
                    error_process["0.0.0.0"] = process_on_port["0.0.0.0"]
                    fail = True
                elif (
                    ip
                    and ip in process_on_port
                    and not re.match(process, process_on_port[ip]["name"])
                ):
                    error_process[ip] = process_on_port[ip]
                    fail = True
                elif not ip:
                    for proc_ip, proc in process_on_port.items():
                        if not re.match(process, proc["name"]):
                            error_process[proc_ip] = proc
                            fail = True

            if fail:
                if ip:
                    fail_msg += " on {}:{}".format(ip, port)
                else:
                    fail_msg += " on {}".format(port)

                if error_process:
                    fail_msg += " but {}".format(
                        " and ".join(
                            "{}({}) listen on {}".format(
                                proc["name"], proc["pid"], proc_ip
                            )
                            for proc_ip, proc in error_process.items()
                        )
                    )
                else:
                    fail_msg += " but nothing listening"

                failures.append(fail_msg)
                continue

            # Success
            failures = []
            break

        if failures:
            errors.append(" or ".join(failures) + ".")

    error_msg = "\n".join(errors)
    if error_msg and raises:
        raise CheckError(error_msg)

    return error_msg or True


def sysctl(params, raises=True):
    """Check if the given sysctl key-values match the ones in memory and
    return a string (or raise if `raises` is set to `True`) with the list
    of non-matching parameters.

    Arguments:
        params (dict): the sysctl parameters to check keyed by name and with
            expected values as values.
        raises (bool): the method will raise if there is any non-matching
            sysctl value.
    """
    errors = []

    for key, value in params.items():
        current_value = __salt__["sysctl.get"](key)
        if current_value != str(value):
            errors.append(
                "Incorrect value for sysctl '{0}', expecting '{1}' but "
                "found '{2}'.".format(key, value, current_value)
            )

    error_msg = "\n".join(errors)

    if errors and raises:
        raise CheckError(error_msg)

    return error_msg


def route_exists(destination, raises=True):
    """Check if a route exists for the destination (IP or CIDR).

    NOTE: only supports IPv4 routes.

    Arguments:
        destination (string): the destination IP or CIDR to check.
        raises (bool): the method will raise if there is no route for this
            destination.
    """
    dest_net = ipaddress.IPv4Network(destination)
    error = None
    route_exists = False

    all_routes = __salt__["network.routes"](family="inet")

    for route in all_routes:
        # Check if our destination network is fully included in this route.
        route_net = ipaddress.IPv4Network(
            "{r[destination]}/{r[netmask]}".format(r=route)
        )
        if _is_subnet_of(dest_net, route_net):
            break
        else:
            route_exists |= dest_net.network_address in route_net
    else:
        if route_exists:
            error = (
                "A route was found for {n.network_address}, but it does not "
                "match the full destination network {n.compressed}"
            ).format(n=dest_net)
        else:
            error = "No route exists for {}".format(dest_net.compressed)

    if error and raises:
        raise CheckError(error)

    return error or True


# Helpers {{{
def _is_subnet_of(left, right):
    """Implementation of `subnet_of` method in Python 3.7+ for networks.

    Naively assumes both arguments are `ipaddress.IPNetwork` objects of the
    same IP version.
    """
    return (
        right.network_address <= left.network_address
        and right.broadcast_address >= left.broadcast_address
    )


# }}}
