import { connect } from 'formik';
import * as React from 'react';
import { useEffect } from 'react';
import usePrevious from 'react-use/lib/usePrevious';
import isEqual from 'lodash/isEqual';

function FormikEffectComponent({ onChange, values }): React.ReactElement {
  const prevValues = usePrevious(values);
  useEffect(() => {
    // Don't run effect on form init and if values did not change
    if (
      prevValues &&
      typeof onChange === 'function' &&
      !isEqual(prevValues, values)
    ) {
      onChange({ prevValues, nextValues: values });
    }
  }, [values, onChange, prevValues]);
  return null;
}
const FormikEffect = connect(FormikEffectComponent);
export { FormikEffect };
