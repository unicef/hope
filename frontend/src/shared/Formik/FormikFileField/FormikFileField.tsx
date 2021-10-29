import React from 'react';

export const FormikFileField = ({ field, form }): React.ReactElement => {
  return (
    <input
      type='file'
      accept='image/*'
      onChange={(event) => {
        form.setFieldValue(field.name, event.currentTarget.files[0]);
      }}
    />
  );
};
