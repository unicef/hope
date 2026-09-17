import { useFormikContext } from 'formik';
import type { ReactElement } from 'react';
import { useEffect } from 'react';

export function AutoSubmitFormOnEnter(): ReactElement {
  const { submitForm } = useFormikContext();
  useEffect(() => {
    const handleEnter = (e: KeyboardEvent): void => {
      if (e.key === 'Enter') {
        submitForm();
      }
    };
    window.addEventListener('keypress', handleEnter);
    return () => {
      window.removeEventListener('keypress', handleEnter);
    };
  }, [submitForm]);
  return <></>;
}
