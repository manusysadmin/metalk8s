{% from "metalk8s/map.jinja" import metalk8s with context %}
{% from "metalk8s/repo/macro.sls" import build_image_name with context %}

include:
  - .kubeconfig

Create kube-scheduler Pod manifest:
  metalk8s.static_pod_managed:
    - name: /etc/kubernetes/manifests/kube-scheduler.yaml
    - source: salt://metalk8s/kubernetes/files/control-plane-manifest.yaml
    - config_files:
      - /etc/kubernetes/scheduler.conf
    - context:
        name: kube-scheduler
        image_name: {{ build_image_name("kube-scheduler") }}
        host: {{ grains['metalk8s']['control_plane_ip'] }}
        port: http-metrics
        scheme: HTTP
        command:
        # kubeadm flags {
          - kube-scheduler
          - --authentication-kubeconfig=/etc/kubernetes/scheduler.conf
          - --authorization-kubeconfig=/etc/kubernetes/scheduler.conf
          # Disable this as 127.0.0.1 from kubeadm as we need to bind this one
          # on the control plane ip of the node
          #- --bind-address=127.0.0.1
          - --kubeconfig=/etc/kubernetes/scheduler.conf
          - --leader-elect=true
          - --port=0
        # }
          - --bind-address={{ grains['metalk8s']['control_plane_ip'] }}
          - --v={{ 2 if metalk8s.debug else 0 }}
        requested_cpu: 100m
        ports:
          - name: http-metrics
            containerPort: 10251
        volumes:
          - path: /etc/kubernetes/scheduler.conf
            name: kubeconfig
            type: File
    - require:
      - metalk8s_kubeconfig: Create kubeconfig file for scheduler
