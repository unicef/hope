import { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

//TODO:
// - add constant with all messages

export function useSnackbarHelper() {
  const history = useHistory();
  const [show, setShow] = useState(
    history.location.state ? history.location.state.showSnackbar : false,
  );
  const message = history.location.state ? history.location.state.message : '';

  useEffect(() => {
    if (history.location.state && history.location.state.showSnackbar) {
        const state = { ...history.location.state };
        delete state.showSnackbar;
        history.replace({ ...history.location, state });
    }
  })

  return {
    show,
    setShow,
    message,
  };
}
