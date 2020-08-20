import React from 'react';
import { FormControlLabel, Checkbox } from '@material-ui/core';

export const Check = ({
  field,
  form,
  label,
  ...otherProps
}): React.ReactElement => {
  const handleChange = (event) => {
    form.setFieldValue(field.name, !field.value);
  };

  return (
    <FormControlLabel
      control={
        <Checkbox
          {...otherProps}
          color='primary'
          checked={field.value}
          onChange={handleChange}
        />
      }
      label={label}
    />
  );
};
