import { useFormikContext } from 'formik';
import React, { useEffect } from 'react';

export const AutoSubmitFormOnEnter = (): React.ReactElement => {
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
};
