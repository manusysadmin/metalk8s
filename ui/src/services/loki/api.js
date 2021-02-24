//@flow
import ApiClient from '../ApiClient';

let lokiApiClient: ?ApiClient = null;

export function initialize(apiUrl: string) {
  lokiApiClient = new ApiClient({ apiUrl });
}

export function getAlertsLoki() {
  if (!lokiApiClient) {
    throw new Error('lokiApiClient should be defined');
  }

  return lokiApiClient.get('/api/v2/alerts').then((resolve) => {
    if (resolve.error) {
      throw resolve.error;
    }
    return resolve;
  });
}

export function getLokiConfig() {
  if (!lokiApiClient) {
    throw new Error('lokiApiClient should be defined');
  }

  return lokiApiClient.get('/config').then((resolve) => {
    if (resolve.error) {
      throw resolve.error;
    }
    return resolve;
  });
}

// TODO:
export const checkHistoryAlertProvider = (): Promise<{
  status: 'healthy' | 'critical',
  retention: number,
}> => {
  return getLokiConfig().then((result) => {});
};
