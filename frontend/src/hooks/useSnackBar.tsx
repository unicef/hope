import React, {
  useState,
  createContext,
  ReactElement,
  useContext,
} from 'react';
import { Snackbar, SnackbarContent as Content } from '@material-ui/core';

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
        <Snackbar open={show} autoHideDuration={5000} onClose={hideMessage}>
          <Content
            message={message}
            // data-cy={snackBar.dataCy}
          />
        </Snackbar>
      </>
    </SnackbarContext.Provider>
  );
};

export const useSnackbar = (): SnackbarContent => useContext(SnackbarContext);
