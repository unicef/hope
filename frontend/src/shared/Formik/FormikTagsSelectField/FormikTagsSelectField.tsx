import React from 'react';
import { TextField } from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';

export const FormikTagsSelectField = ({
  field,
  form,
  label,
  type,
  precision,
  ...otherProps
}): React.ReactElement => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];

  const onBlur = (e): void => {
    const newEvent = { ...e };
    if (type === 'number' && precision !== undefined) {
      newEvent.target.value = parseFloat(e.target.value).toFixed(2);
    }
    form.handleBlur(newEvent);
  };

  return (
    <>
      <Autocomplete
        {...field}
        {...otherProps}
        multiple
        name={field.name}
        id='tags-standard'
        options={[]}
        value={field.value}
        onChange={form.handleChange}
        freeSolo
        placeholder={label}
        renderInput={(params) => {
          return (
            <TextField
              {...params}
              id={`textField-${field.name}`}
              margin='dense'
              onBlur={onBlur}
              error={isInvalid}
              helperText={isInvalid && form.errors[field.name]}
              variant='filled'
              label={label}
            />
          );
        }}
      />
    </>
  );
};
