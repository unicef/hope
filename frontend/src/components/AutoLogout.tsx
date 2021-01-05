import React from 'react';
import IdleTimer from 'react-idle-timer';
import { AUTO_LOGOUT_MILLIS } from '../config';

export const AutoLogout = (): React.ReactElement => {
  const onIdle = (): void => {
    if (!localStorage.getItem('AUTHENTICATED')) {
      return;
    }
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
  };
  return (
    <IdleTimer onIdle={onIdle} debounce={250} timeout={AUTO_LOGOUT_MILLIS} />
  );
};
