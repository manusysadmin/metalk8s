import {
  removeWarningAlerts,
  isSubObject,
  getActiveAlerts,
  getHealthStatus,
} from './alertUtils';
import { alerts } from './alertUtilsData';

it('should return the alert list fitered the warning alert', () => {
  const result = removeWarningAlerts(alerts);
  expect(result).toStrictEqual([
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
  ]);
});

it('should return true when obj2 is the subset of obj1', () => {
  const obj = { firstname: 'Garfield', lastname: 'Madalyn' };
  const subObj = { firstname: 'Garfield' };
  const result = isSubObject(obj, subObj);
  expect(result).toEqual(true);
});

it('should return false when there is a different value in obj2', () => {
  const obj = { firstname: 'Garfield', lastname: 'Madalyn' };
  const subObj = { firstname: 'Garfield', lastname: 'Doretta' };
  const result = isSubObject(obj, subObj);
  expect(result).toEqual(false);
});

it('should return false when obj2 has a different property', () => {
  const obj = { firstname: 'Garfield', lastname: 'Madalyn' };
  const subObj = { firstname: 'Garfield', name: 'Madalyn' };
  const result = isSubObject(obj, subObj);
  expect(result).toEqual(false);
});

it('should return false when obj2 has an extra property', () => {
  const obj = { firstname: 'Garfield', lastname: 'Madalyn' };
  const subObj = { firstname: 'Garfield', lastname: 'Madalyn', age: 26 };
  const result = isSubObject(obj, subObj);
  expect(result).toEqual(false);
});

it('filters the alert base on the labels', async () => {
  const selectors = {
    instance: '192.168.1.6:9100',
    severity: 'warning',
    device: '/dev/vdc2',
  };
  const result = await getActiveAlerts(alerts, selectors);
  const alert = [
    {
      id: 'NodeFilesystemAlmostOutOfSpace',
      summary: 'Filesystem has less than 5% space left.',
      description:
        'Filesystem on /dev/vdc2 at 192.168.1.6:9100 has only 0.00% available space left.',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: 'warning',
      originalAlert: {
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
      documentationUrl:
        'https://github.com/kubernetes-monitoring/kubernetes-mixin/tree/master/runbook.md#alert-name-nodefilesystemalmostoutofspace',
    },
  ];
  expect(result).toStrictEqual(alert);
});

it('should return warning for during the time when warning alert was firing', () => {
  const alerts = [
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: 'warning',
      originalAlert: {},
    },
  ];
  const result = getHealthStatus(alerts, '2021-01-18T20:43:35.358Z');
  expect(result).toEqual('warning');
});

it('should return warning status during the time when warning alert was firing but no critical alert', () => {
  const alerts = [
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: 'warning',
      originalAlert: {},
    },
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2020-01-18T16:43:35.358Z',
      endsAt: '2020-01-21T09:32:35.358Z',
      severity: 'critical',
      originalAlert: {},
    },
  ];
  const result = getHealthStatus(alerts, '2021-01-18T20:43:35.358Z');
  expect(result).toEqual('warning');
});

it('should return critical status during the time when critical alert and warning alert are both firing', () => {
  const alerts = [
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: 'warning',
      originalAlert: {},
    },
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: 'critical',
      originalAlert: {},
    },
  ];
  const result = getHealthStatus(alerts, '2021-01-18T20:43:35.358Z');
  expect(result).toEqual('critical');
});

it('should return healthy when only watchdog alert fired', () => {
  const alerts = [
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: 'none',
      originalAlert: {},
    },
  ];
  const result = getHealthStatus(alerts, '2021-01-18T20:43:35.358Z');
  expect(result).toEqual('healthy');
});

it('should return healthy for current status when all the alerts were on the past', () => {
  const alerts = [
    {
      id: '',
      summary: '',
      description: '',
      startsAt: '2021-01-18T16:43:35.358Z',
      endsAt: '2021-01-21T09:32:35.358Z',
      severity: '',
      originalAlert: {},
    },
  ];
  const result = getHealthStatus(alerts, new Date().toISOString());
  expect(result).toEqual('healthy');
});
