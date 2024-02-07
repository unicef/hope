import * as React from 'react';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { get } from 'lodash';
import { removeBracketsAndQuotes } from '@utils/utils';

export const useSnackbar = (): {
  show;
  setShow;
  message;
  showMessage;
  dataCy?;
} => {
  const navigate = useNavigate();
  const location = useLocation();
  const [show, setShow] = useState(
    location.state ? location.state.showSnackbar : false,
  );
  const [message, setMessage] = useState(
    location.state ? location.state.message : '',
  );
  const dataCy = location.state ? location.state.dataCy : '';

  useEffect(() => {
    if (location.state && location.state.showSnackbar) {
      setShow(true);
      setMessage(location.state.message);
      history.replace({
        ...location,
        state: { ...location.state, showSnackbar: false },
      });
    }
  }, [location, history]);

  const showMessage = (
    messageContent: string,
    options?: {
      pathname?: string;
      historyMethod?: keyof typeof history;
      dataCy?: string;
    },
  ): void => {
    const formattedMessage = removeBracketsAndQuotes(messageContent);
    setShow(true);
    setMessage(formattedMessage);
    history[get(options, 'historyMethod', 'replace')]({
      pathname: get(options, 'pathname', history.location.pathname),
      state: {
        showSnackbar: true,
        message: formattedMessage,
        dataCy: get(options, 'dataCy'),
      },
    });
    navigate(get(options, 'pathname', history.location.pathname));
  };

  return {
    show,
    setShow,
    message,
    showMessage,
    dataCy,
  };
};
