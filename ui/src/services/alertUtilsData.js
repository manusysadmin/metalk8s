// the real alerts object for tesing
export const alerts = [
  {
    annotations: {
      description:
        'Filesystem on /dev/vdc2 at 192.168.1.6:9100 has only 0.00% available space left.',
      runbook_url:
        'https://github.com/kubernetes-monitoring/kubernetes-mixin/tree/master/runbook.md#alert-name-nodefilesystemalmostoutofspace',
      summary: 'Filesystem has less than 3% space left.',
    },
    endsAt: '2021-01-21T09:32:35.358Z',
    fingerprint: '5ef4c93e954ac2c9',
    receivers: [
      {
        name: 'null',
      },
    ],
    startsAt: '2021-01-18T16:43:35.358Z',
    status: {
      inhibitedBy: [],
      silencedBy: [],
      state: 'active',
    },
    updatedAt: '2021-01-21T09:28:40.099Z',
    generatorURL:
      'http://prometheus-operator-prometheus.metalk8s-monitoring:9090/graph?g0.expr=%28node_filesystem_avail_bytes%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%2F+node_filesystem_size_bytes%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%2A+100+%3C+3+and+node_filesystem_readonly%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%3D%3D+0%29&g0.tab=1',
    labels: {
      alertname: 'NodeFilesystemAlmostOutOfSpace',
      container: 'node-exporter',
      device: '/dev/vdc2',
      endpoint: 'metrics',
      fstype: 'ext4',
      instance: '192.168.1.6:9100',
      job: 'node-exporter',
      mountpoint: '/mnt/testpart2',
      namespace: 'metalk8s-monitoring',
      pod: 'prometheus-operator-prometheus-node-exporter-m9qcj',
      prometheus: 'metalk8s-monitoring/prometheus-operator-prometheus',
      service: 'prometheus-operator-prometheus-node-exporter',
      severity: 'critical',
    },
  },
  {
    annotations: {
      description:
        'Filesystem on /dev/vdc2 at 192.168.1.6:9100 has only 0.00% available space left.',
      runbook_url:
        'https://github.com/kubernetes-monitoring/kubernetes-mixin/tree/master/runbook.md#alert-name-nodefilesystemalmostoutofspace',
      summary: 'Filesystem has less than 5% space left.',
    },
    endsAt: '2021-01-21T09:32:35.358Z',
    fingerprint: '6331188d982cdcfc',
    receivers: [
      {
        name: 'null',
      },
    ],
    startsAt: '2021-01-18T16:43:35.358Z',
    status: {
      inhibitedBy: [],
      silencedBy: [],
      state: 'active',
    },
    updatedAt: '2021-01-21T09:28:40.092Z',
    generatorURL:
      'http://prometheus-operator-prometheus.metalk8s-monitoring:9090/graph?g0.expr=%28node_filesystem_avail_bytes%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%2F+node_filesystem_size_bytes%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%2A+100+%3C+5+and+node_filesystem_readonly%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%3D%3D+0%29&g0.tab=1',
    labels: {
      alertname: 'NodeFilesystemAlmostOutOfSpace',
      container: 'node-exporter',
      device: '/dev/vdc2',
      endpoint: 'metrics',
      fstype: 'ext4',
      instance: '192.168.1.6:9100',
      job: 'node-exporter',
      mountpoint: '/mnt/testpart2',
      namespace: 'metalk8s-monitoring',
      pod: 'prometheus-operator-prometheus-node-exporter-m9qcj',
      prometheus: 'metalk8s-monitoring/prometheus-operator-prometheus',
      service: 'prometheus-operator-prometheus-node-exporter',
      severity: 'warning',
    },
  },
  {
    annotations: {
      description:
        'Filesystem on /dev/vdc1 at 192.168.1.6:9100 has only 3.28% available space left.',
      runbook_url:
        'https://github.com/kubernetes-monitoring/kubernetes-mixin/tree/master/runbook.md#alert-name-nodefilesystemalmostoutofspace',
      summary: 'Filesystem has less than 5% space left.',
    },
    endsAt: '2021-01-21T09:32:35.358Z',
    fingerprint: '6c9be09b96993ce4',
    receivers: [
      {
        name: 'null',
      },
    ],
    startsAt: '2021-01-18T16:43:35.358Z',
    status: {
      inhibitedBy: [],
      silencedBy: [],
      state: 'active',
    },
    updatedAt: '2021-01-21T09:28:40.092Z',
    generatorURL:
      'http://prometheus-operator-prometheus.metalk8s-monitoring:9090/graph?g0.expr=%28node_filesystem_avail_bytes%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%2F+node_filesystem_size_bytes%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%2A+100+%3C+5+and+node_filesystem_readonly%7Bfstype%21%3D%22%22%2Cjob%3D%22node-exporter%22%7D+%3D%3D+0%29&g0.tab=1',
    labels: {
      alertname: 'NodeFilesystemAlmostOutOfSpace',
      container: 'node-exporter',
      device: '/dev/vdc1',
      endpoint: 'metrics',
      fstype: 'xfs',
      instance: '192.168.1.6:9100',
      job: 'node-exporter',
      mountpoint: '/mnt/testpart1',
      namespace: 'metalk8s-monitoring',
      pod: 'prometheus-operator-prometheus-node-exporter-m9qcj',
      prometheus: 'metalk8s-monitoring/prometheus-operator-prometheus',
      service: 'prometheus-operator-prometheus-node-exporter',
      severity: 'warning',
    },
  },
];
