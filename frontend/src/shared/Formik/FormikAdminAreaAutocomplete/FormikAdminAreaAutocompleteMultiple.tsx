import React from 'react';
import { AdminAreaAutocompleteMultiple } from '../../autocompletes/AdminAreaAutocompleteMultiple';

export const FormikAdminAreaAutocompleteMultiple = ({
  field,
  form,
  disabled,
}): React.ReactElement => {
  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option);
    }
  };
  return (
    <>
      <AdminAreaAutocompleteMultiple
        disabled={disabled}
        value={field.value}
        onChange={handleChange}
      />
    </>
  );
};
