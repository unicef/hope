import React, {
  createContext,
  ReactElement,
  useContext,
  useState,
} from 'react';
import Snackbar from '@mui/material/Snackbar';

type SnackbarContent = {
  message: string;
  showMessage: (msg: string) => void;
};

export const SnackbarContext = createContext<SnackbarContent>({
  message: '',
  showMessage: (): void => null,
});

export const SnackbarProvider = ({ children }): ReactElement => {
  const [show, setShow] = useState(false);
  const [message, setMessage] = useState('');

  const removeBracketsAndQuotes = (str: string): string => {
    let modifiedStr = str;
    modifiedStr = modifiedStr.replace(/\[|\]|"|'/g, '');
    return modifiedStr;
  };

  const showMessage = (msg: string): void => {
    setShow(true);
    setMessage(removeBracketsAndQuotes(msg));
  };

  const hideMessage = (): void => {
    setShow(false);
    setMessage('');
  };

  return (
    <SnackbarContext.Provider value={{ showMessage, message }}>
      <>
        {children}
        <Snackbar
          open={show}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          autoHideDuration={5000}
          onClose={hideMessage}
          message={message}
        />
      </>
    </SnackbarContext.Provider>
  );
};

export const useSnackbar = (): SnackbarContent => useContext(SnackbarContext);
