import React, {useEffect, useRef, useState} from 'react';
import IdleTimer from 'react-idle-timer';
import {AUTO_LOGOUT_MILLIS} from '../config';

export const AutoLogout = (): React.ReactElement => {
  const idleTimer = useRef(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [bc, setBc] = useState(
    () => new BroadcastChannel('auto-logout-channel'),
  );
  useEffect(() => {
    if (!bc) {
      return;
    }
    bc.onmessage = () => idleTimer.current.reset();
  }, [bc]);
  const onIdle = (): void => {
    if (!localStorage.getItem('AUTHENTICATED')) {
      return;
    }
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
  };
  const onAction = (): void => {
    bc.postMessage('active');
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
