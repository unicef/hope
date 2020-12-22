import React, { useRef, useState } from 'react';
import IdleTimer from 'react-idle-timer';

export const AutoLogout = (): React.ReactElement => {
  let countdownInterval;
  let timeout;
  const fifteenMinutes = 1000 * 60 * 15;
  //eslint-disable-next-line
  const [timeoutCountdown, setTimeoutCountdown] = useState(0);
  const idleTimer = useRef(null);
  const clearSessionTimeout = (): void => {
    clearTimeout(timeout);
  };
  const clearSessionInterval = (): void => {
    clearInterval(countdownInterval);
  };
  const handleLogout = (): void => {
    clearSessionInterval();
    clearSessionTimeout();
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
  };
  const onActive = (): void => {
    clearSessionInterval();
    clearSessionTimeout();
  };
  const onIdle = (): void => {
    const delay = 1000 * 1;
    if (localStorage.getItem('AUTHENTICATED') !== null) {
      timeout = setTimeout(() => {
        let countDown = 10;
        setTimeoutCountdown(countDown);
        countdownInterval = setInterval(() => {
          if (countDown > 0) {
            //eslint-disable-next-line
            setTimeoutCountdown(--countDown);
          } else {
            handleLogout();
          }
        }, 1000);
      }, delay);
    }
  };
  return (
    <IdleTimer
      ref={idleTimer}
      onActive={onActive}
      onIdle={onIdle}
      debounce={250}
      timeout={fifteenMinutes}
    />
  );
};
