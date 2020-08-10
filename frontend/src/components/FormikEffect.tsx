import { connect } from 'formik';
import { useEffect } from 'react';
import usePrevious from 'react-use/lib/usePrevious';

const FormikEffectComponent = ({ onChange, values }) => {
  const prevValues = usePrevious(values);
  useEffect(() => {
    // Don't run effect on form init
    if (prevValues && typeof onChange === 'function') {
      onChange({ prevValues, nextValues: values });
    }
  }, [values, onChange, prevValues]);
  return null;
};
const FormikEffect = connect(FormikEffectComponent);
export { FormikEffect };
