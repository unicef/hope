import React, { useRef } from 'react';
import IdleTimer from 'react-idle-timer';
import { AUTO_LOGOUT_MILLIS } from '../../config';

export const AutoLogout = (): React.ReactElement => {
  const idleTimer = useRef(null);

  const onIdle = (): void => {
    if (!localStorage.getItem('AUTHENTICATED')) {
      return;
    }
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
  };

  const onAction = (): void => {
    idleTimer.current.reset();
  };

  return (
    <IdleTimer
      ref={idleTimer}
      onAction={onAction}
      onIdle={onIdle}
      debounce={500}
      timeout={AUTO_LOGOUT_MILLIS}
    />
  );
};
