//@flow
import ApiClient from '../ApiClient';
import { STATUS_CRITICAL, STATUS_HEALTH } from '../../constants';

let alertmanagerApiClient: ?ApiClient = null;

export function initialize(apiUrl: string) {
  alertmanagerApiClient = new ApiClient({ apiUrl });
}
export type PrometheusAlert = {
  annotations: {
    [key: string]: string,
  },
  receivers: {
    name: string,
  }[],
  fingerprint: string,
  startsAt: string,
  updatedAt: string,
  endsAt: string,
  status: {
    state: 'unprocessed' | 'active' | 'suppressed',
    silencedBy: string[],
    inhibitedBy: string[],
  },
  labels: {
    [key: string]: string,
  },
  generatorURL: string,
};

export function getAlerts() {
  if (!alertmanagerApiClient) {
    throw new Error('alertmanagerApiClient should be defined');
  }

  return alertmanagerApiClient.get('/api/v2/alerts').then((resolve) => {
    if (resolve.error) {
      throw resolve.error;
    }
    return resolve;
  });
}

export const checkActiveAlertProvider = (): Promise<{
  status: 'healthy' | 'critical',
}> => {
  // depends on Watchdog to see the if Alertmanager is up
  return getAlerts().then((result) => {
    const watchdog = result.find(
      (alert) => alert.labels.alertname === 'Watchdog',
    );
    if (watchdog) return STATUS_HEALTH;
    else return STATUS_CRITICAL;
  });
};
