import { useEffect } from 'react';
import { showApiErrorMessages } from '@utils/utils';
import { useSnackbar } from '@hooks/useSnackBar';

// Surfaces a failed query through the snackbar, so a component never renders an
// empty field with no explanation of why the data is missing.
export function useApiErrorSnackbar(isError: boolean, error: unknown): void {
  const { showMessage } = useSnackbar();

  useEffect(() => {
    if (isError) {
      showApiErrorMessages(error, showMessage);
    }
  }, [isError, error, showMessage]);
}
