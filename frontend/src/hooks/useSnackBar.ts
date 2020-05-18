import { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import get from 'lodash/get';

export function useSnackbar(): { show; setShow; message; showMessage; dataCy?; } {
  const history = useHistory();
  const location = useLocation();
  const [show, setShow] = useState(
    location.state ? location.state.showSnackbar : false,
  );
  const message = location.state ? location.state.message : '';
  const dataCy = location.state ? location.state.dataCy : '';
  useEffect(() => {
    if (location.state && location.state.showSnackbar) {
      setShow(true);
      history.replace({
        ...location,
        state: { ...location.state, showSnackbar: false },
      });
    }
  }, [location, history]);

  const showMessage = (
    messageContent: string,
    options?: { pathname?: string; historyMethod?: keyof typeof history, dataCy?: string, },
  ): void => {
    history[get(options, 'historyMethod', 'replace')]({
      pathname: get(options, 'pathname', history.location.pathname),
      state: { showSnackbar: true, message: messageContent, dataCy: options.dataCy },
    });
  };

  return {
    show,
    setShow,
    message,
    showMessage,
    dataCy
  };
}
