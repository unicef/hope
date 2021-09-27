import { Box } from '@material-ui/core';
import React from 'react';
import InputLabel from '../../InputLabel';

export const FormikFileField = ({
  field,
  form,
  ...otherProps
}): React.ReactElement => {
  return (
    <>
      <Box mb={1}>
        <InputLabel>{otherProps.label}</InputLabel>
      </Box>
      <input
        type='file'
        accept='image/*'
        onChange={(event) => {
          form.setFieldValue(field.name, event.currentTarget.files[0]);
        }}
      />
    </>
  );
};
