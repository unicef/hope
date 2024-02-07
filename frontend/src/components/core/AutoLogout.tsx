import React, { useEffect } from 'react';
import { useIdleTimer } from 'react-idle-timer';
import { AUTO_LOGOUT_MILLIS } from '../../config';

export function AutoLogout(): React.ReactElement {
  const handleOnIdle = (): void => {
    if (!localStorage.getItem('AUTHENTICATED')) {
      return;
    }
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
  };

  //eslint-disable-next-line
  const { reset } = useIdleTimer({
    timeout: AUTO_LOGOUT_MILLIS,
    onIdle: handleOnIdle,
    debounce: 500,
  });

  const handleOnAction = (): void => {
    reset();
  };

  useEffect(() => {
    window.addEventListener('click', handleOnAction);
    window.addEventListener('mousemove', handleOnAction);

    return () => {
      window.removeEventListener('click', handleOnAction);
      window.removeEventListener('mousemove', handleOnAction);
    };
  }, [handleOnAction]);

  return <></>;
}
