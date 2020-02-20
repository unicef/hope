import { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

export function useSnackbarHelper() {
  const history = useHistory();
  const location = useLocation();
  const [show, setShow] = useState(
    location.state ? location.state.showSnackbar : false,
  );
  const message = location.state ? location.state.message : '';
  useEffect(() => {
    if (location.state && location.state.showSnackbar) {
      setShow(true);
      history.replace({
        ...location,
        state: { ...location.state, showSnackbar: false },
      });
    }
  }, [location, history]);

  return {
    show,
    setShow,
    message,
  };
}
