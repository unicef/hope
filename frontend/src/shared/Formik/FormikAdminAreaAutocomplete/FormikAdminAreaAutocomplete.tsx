import React from 'react';
import { AdminAreasAutocomplete } from '../../../components/population/AdminAreaAutocomplete';

export const FormikAdminAreaAutocomplete = ({
  field,
  form,
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
      <AdminAreasAutocomplete value={field.value} onChange={handleChange} />
    </>
  );
};
