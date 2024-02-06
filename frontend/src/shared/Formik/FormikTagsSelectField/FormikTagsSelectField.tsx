import React from 'react';
import { TextField } from '@mui/material';
import Autocomplete from '@mui/lab/Autocomplete';

export function FormikTagsSelectField({
  field,
  form,
  label,
  type,
  precision,
  ...otherProps
}): React.ReactElement {
  const isInvalid = form.errors[field.name] && form.touched[field.name];

  const onBlur = (e): void => {
    const newEvent = { ...e };
    if (type === 'number' && precision !== undefined) {
      newEvent.target.value = parseFloat(e.target.value).toFixed(2);
    }
    form.handleBlur(newEvent);
  };

  return (
    <Autocomplete
      {...field}
      {...otherProps}
      multiple
      name={field.name}
      id="tags-standard"
      options={[]}
      value={field.value}
      onChange={form.handleChange}
      freeSolo
      placeholder={label}
      renderInput={(params) => (
        <TextField
          {...params}
          id={`textField-${field.name}`}
          margin="dense"
          onBlur={onBlur}
          error={isInvalid}
          helperText={isInvalid && form.errors[field.name]}
          variant="outlined"
          label={label}
        />
      )}
    />
  );
}
