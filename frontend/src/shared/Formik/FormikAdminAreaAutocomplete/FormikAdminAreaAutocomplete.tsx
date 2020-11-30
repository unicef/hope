import React from 'react';
import { AdminAreasAutocomplete } from '../../../components/population/AdminAreaAutocomplete';

export const FormikAdminAreaAutocomplete = ({
  field,
  form,
  disabled
}): React.ReactElement => {
  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, undefined);
    } else {
      form.setFieldValue(field.name, option.node.title);
    }
  };
  return (
    <>
      <AdminAreasAutocomplete disabled={disabled} value={field.value} onChange={handleChange} />
    </>
  );
};
