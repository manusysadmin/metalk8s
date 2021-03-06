@post @ci @local @sanity
Feature: Cluster Sanity Checks
    A set of basic sanity checks to verify a MetalK8s cluster is in good shape.

    Background:
        Given the Kubernetes API is available

    Scenario: List Pods
        Then the 'pods' list should not be empty in the 'kube-system' namespace

    Scenario: Exec in Pods
        Then we can exec 'true' in a pod labeled 'app=salt-master' in the 'kube-system' namespace

    Scenario: Read Pod logs
        Then we can read logs from all containers in a pod labeled 'app=salt-master' in the 'kube-system' namespace

    Scenario Outline: Static Pod runs where expected
        Then the static Pod <name> in the <namespace> namespace runs on <role> nodes

        Examples:
        | namespace   | name                    | role      |
        | kube-system | repositories            | bootstrap |
        | kube-system | salt-master             | bootstrap |
        | kube-system | kube-apiserver          | master    |
        | kube-system | kube-controller-manager | master    |
        | kube-system | kube-scheduler          | master    |
        | kube-system | etcd                    | etcd      |
        | kube-system | apiserver-proxy         | all       |

    Scenario Outline: Deployment has available replicas
        Then the Deployment <name> in the <namespace> namespace has all desired replicas available

        Examples:
        | namespace           | name                                   |
        | kube-system         | calico-kube-controllers                |
        | kube-system         | coredns                                |
        | kube-system         | storage-operator                       |
        | metalk8s-auth       | dex                                    |
        | metalk8s-ingress    | ingress-nginx-defaultbackend           |
        | metalk8s-monitoring | prometheus-adapter                     |
        | metalk8s-monitoring | prometheus-operator-grafana            |
        | metalk8s-monitoring | prometheus-operator-kube-state-metrics |
        | metalk8s-monitoring | prometheus-operator-operator           |
        | metalk8s-ui         | metalk8s-ui                            |

    Scenario Outline: DaemonSet has desired Pods ready
        Then the DaemonSet <name> in the <namespace> namespace has all desired Pods ready

        Examples:
        | namespace           | name                                         |
        | kube-system         | calico-node                                  |
        | kube-system         | kube-proxy                                   |
        | metalk8s-ingress    | ingress-nginx-controller                     |
        | metalk8s-ingress    | ingress-nginx-control-plane-controller       |
        | metalk8s-monitoring | prometheus-operator-prometheus-node-exporter |
        | metalk8s-logging    | fluent-bit                                   |

    @volumes_provisioned
    Scenario Outline: StatefulSet has available replicas
        Then the StatefulSet <name> in the <namespace> namespace has all desired replicas available

        Examples:
        | namespace           | name                                          |
        | metalk8s-monitoring | alertmanager-prometheus-operator-alertmanager |
        | metalk8s-monitoring | prometheus-prometheus-operator-prometheus     |
        | metalk8s-logging    | loki                                          |
