import React, {
  createContext,
  ReactElement,
  useContext,
  useState,
} from 'react';
import Snackbar from '@mui/material/Snackbar';
import { useTranslation } from 'react-i18next';

type SnackbarContent = {
  message: string;
  showMessage: (msg: string) => void;
  showRestApiError: (error: Error, defaultMessage?: string) => void;
};

export const SnackbarContext = createContext<SnackbarContent>({
  message: '',
  showMessage: (): void => null,
  showRestApiError: (): void => null,
});

export const SnackbarProvider = ({ children }): ReactElement => {
  const [show, setShow] = useState(false);
  const [message, setMessage] = useState('');
  const { t } = useTranslation();

  const removeBracketsAndQuotes = (str: string): string => {
    let modifiedStr = str;
    modifiedStr = modifiedStr.replace(/\[|\]|"|'/g, '');
    return modifiedStr;
  };

  const showMessage = (msg: string): void => {
    setShow(true);
    setMessage(removeBracketsAndQuotes(msg));
  };

  const showRestApiError = (error: Error, defaultMessage?: string): void => {
    let errorMessage = t(
      defaultMessage || 'An error occurred while executing this operation.',
    );
    try {
      const errrorWithBody = error as any;
      errorMessage = errrorWithBody.message;
    } catch (_) {
      /* empty */
    }
    try {
      const errrorWithBody = error as any;
      errorMessage = errrorWithBody.body.join('\n');
    } catch (_) {
      /* empty */
    }
    showMessage(errorMessage);
  };

  const hideMessage = (): void => {
    setShow(false);
    setMessage('');
  };

  return (
    <SnackbarContext.Provider
      value={{ showMessage, message, showRestApiError }}
    >
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
