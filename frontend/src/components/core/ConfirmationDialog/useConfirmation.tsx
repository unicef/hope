import React, {
  createContext,
  ReactNode,
  useContext,
  useRef,
  useState,
} from 'react';
import { ConfirmationDialog, ConfirmationDialogOptions } from './ConfirmationDialog';

const ConfirmationDialogContext = createContext<
  (options: ConfirmationDialogOptions) => Promise<void>
>(Promise.reject.bind(Promise));

export const useConfirmation = (): ((
  options: ConfirmationDialogOptions,
) => Promise<void>) => useContext(ConfirmationDialogContext);

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export const ConfirmationDialogProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [
    confirmationState,
    setConfirmationState,
  ] = useState<ConfirmationDialogOptions | null>(null);

  const awaitingPromiseRef = useRef<{
    resolve: () => void;
    reject: () => void;
  }>();

  const openConfirmation = ({
    catchOnCancel = false,
    ...otherOptions
  }: ConfirmationDialogOptions): Promise<void> => {
    setConfirmationState({ catchOnCancel, ...otherOptions });
    return new Promise<void>((resolve, reject) => {
      awaitingPromiseRef.current = { resolve, reject };
    });
  };

  const handleClose = (): void => {
    if (confirmationState?.catchOnCancel && awaitingPromiseRef.current) {
      awaitingPromiseRef.current.reject();
    }

    setConfirmationState(null);
  };

  const handleSubmit = (): void => {
    if (awaitingPromiseRef.current) {
      awaitingPromiseRef.current.resolve();
    }

    setConfirmationState(null);
  };

  return (
    <ConfirmationDialogContext.Provider value={openConfirmation}>
      {children}
      <ConfirmationDialog
        open={!!confirmationState}
        onSubmit={handleSubmit}
        onClose={handleClose}
        {...confirmationState}
      />
    </ConfirmationDialogContext.Provider>
  );
};
