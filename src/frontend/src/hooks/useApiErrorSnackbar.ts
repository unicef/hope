import { useEffect, useRef } from 'react';
import { showApiErrorMessages } from '@utils/utils';
import { useSnackbar } from '@hooks/useSnackBar';

// Surfaces a failed query through the snackbar, so a component never renders an
// empty field with no explanation of why the data is missing.
export function useApiErrorSnackbar(isError: boolean, error: unknown): void {
  const { showMessage } = useSnackbar();
  const reported = useRef<unknown>(null);

  useEffect(() => {
    if (isError && reported.current !== error) {
      reported.current = error;
      showApiErrorMessages(error, showMessage);
    }
    if (!isError) {
      reported.current = null;
    }
    // showMessage omitted on purpose: new closure on every provider render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isError, error]);
}
