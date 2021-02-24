//@flow
import { STATUS_CRITICAL, STATUS_WARNING, STATUS_HEALTH } from '../constants';
import { getAlertsLoki } from './loki/api';
import type { Health } from './NodeVolumesUtils';
import type { PrometheusAlert } from './alertmanager/api';

type AlertList = {
  id: string,
  summary: string,
  description: string,
  startsAt: string,
  endsAt: string,
  severity: string,
  originalAlert: {},
  documentationUrl?: string,
}[];

// Return boolean to tell if the two alerts are the same only with different severity
const isSameAlertWithDiffSeverity = (
  alert1: $PropertyType<PrometheusAlert, 'labels'>,
  alert2: $PropertyType<PrometheusAlert, 'labels'>,
): boolean => {
  // Filtering out the `severity` property
  function replacer(key, value) {
    if (key === 'severity') {
      return undefined;
    }
    return value;
  }

  return JSON.stringify(alert1, replacer) === JSON.stringify(alert2, replacer);
};

/*
 ** This function removes the warning alert from the list when critical one is triggered
 ** It should be called at saga level before storing the alerts to `redux-store`
 ** or where we resolve the promise with `react-query`
 */
export const removeWarningAlerts = (
  alerts: Array<PrometheusAlert>,
): Array<PrometheusAlert> => {
  const len = alerts.length;
  const removeIndex = [];
  for (let i = 0; i < len - 1; i++) {
    for (let j = i + 1; j < len; j++) {
      if (isSameAlertWithDiffSeverity(alerts[i].labels, alerts[j].labels)) {
        if (alerts[i].labels.severity === STATUS_WARNING) {
          removeIndex.push(i);
        } else if (alerts[j].labels.severity === STATUS_WARNING) {
          removeIndex.push(j);
        }
      }
    }
  }

  let removedWarningAlerts = [...alerts];
  removeIndex.forEach((index) => removedWarningAlerts.splice(index, 1));

  return removedWarningAlerts;
};

/*  Check if one object is the subset of another object
 ** We will use this function to filter the alerts which selectors is the subset of the alert labels.
 */
export const isSubObject = (
  obj: { [labelName: string]: string },
  subObj: { [labelName: string]: string },
): boolean => {
  const propertyNames = Object.getOwnPropertyNames(subObj);
  for (let i = 0; i < propertyNames.length; i++) {
    const propName = propertyNames[i];
    if (Object.prototype.hasOwnProperty.call(obj, propName)) {
      if (obj[propName] !== subObj[propName]) {
        return false;
      }
      if (
        i === propertyNames.length - 1 &&
        obj[propName] === subObj[propName]
      ) {
        return true;
      }
    } else {
      return false;
    }
  }
  return false;
};

// TODO: Call Loki Endpoint
export const getHistoryAlerts = (
  selectors: { [labelName: string]: string },
  duration: string,
  endDate?: string = new Date().toISOString(),
): AlertList => {
  return getAlertsLoki().filter((alert) =>
    isSubObject(alert.labels, selectors),
  );
};

// Call Alertmanager Endpoint
export const getActiveAlerts = (
  alerts: Array<PrometheusAlert>,
  selectors: {
    [labelName: string]: string,
  },
): AlertList => {
  const result = alerts
    .filter((alert) => {
      return isSubObject(alert.labels, selectors);
    })
    .map((alert) => {
      return {
        id: alert.labels.alertname,
        summary: alert.annotations.summary,
        description: alert.annotations.description || alert.annotations.message,
        startsAt: alert.startsAt,
        endsAt: alert.endsAt || new Date().toISOString(),
        severity: alert.labels.severity,
        originalAlert: alert,
        documentationUrl: alert.annotations.runbook_url,
      };
    });
  return result;
};

// check if the given time is BEFORE the start time, DURING the two, or AFTER the end time.
export const firingTime = (
  start: string,
  end: string,
  on: string,
): 'BEFORE' | 'DURING' | 'AFTER' => {
  const onTS = new Date(on).getTime();
  const startTS = new Date(start).getTime();
  const endTS = new Date(end).getTime();
  if (startTS <= onTS && endTS >= onTS) {
    return 'DURING';
  } else if (onTS < startTS) {
    return 'BEFORE';
  } else {
    return 'AFTER';
  }
};

export const getHealthStatus = (
  alerts: AlertList,
  activeOn: string,
): Health => {
  // if there is one critical alert firing, then health status is `STATUS_CRITICAL`
  if (
    alerts.find(
      (alert) =>
        alert.severity === 'critical' &&
        firingTime(alert.startsAt, alert.endsAt, activeOn) === 'DURING',
    )
  ) {
    return STATUS_CRITICAL;
  } else if (
    alerts.find(
      (alert) =>
        alert.severity === 'warning' &&
        firingTime(alert.startsAt, alert.endsAt, activeOn) === 'DURING',
    )
  ) {
    return STATUS_WARNING;
  } else return STATUS_HEALTH;
};
