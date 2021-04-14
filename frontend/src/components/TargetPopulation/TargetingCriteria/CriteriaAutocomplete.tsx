import React, { useState, useEffect } from 'react';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { TextField, Paper } from '@material-ui/core';
import styled from 'styled-components';
import get from 'lodash/get';

const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
`;
interface Option {
  labelEn: string;
}

export function CriteriaAutocomplete({
  field,
  ...otherProps
}): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [newValue, setNewValue] = useState(null);
  useEffect(() => {
    const optionValue =
      otherProps.choices.find((choice) => choice.name === field.value) || null;
    setNewValue(optionValue);
  }, [field.value, otherProps.choices]);

  const isInvalid =
    get(otherProps.form.errors, field.name) &&
    get(otherProps.form.touched, field.name);
  return (
    <StyledAutocomplete<Option>
      {...field}
      {...otherProps}
      open={open}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      options={otherProps.choices}
      value={newValue}
      getOptionLabel={(option) => {
        if (option) {
          return option.labelEn;
        }
        return '';
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          {...otherProps}
          variant='outlined'
          margin='dense'
          fullWidth
          helperText={isInvalid && get(otherProps.form.errors, field.name)}
          error={isInvalid}
          InputProps={{
            ...params.InputProps,
          }}
          // https://github.com/mui-org/material-ui/issues/12805
          // eslint-disable-next-line react/jsx-no-duplicate-props
          inputProps={{
            ...params.inputProps,
            'data-cy': `autocomplete-target-criteria-option-${otherProps.index}`,
          }}
        />
      )}
      data-cy='autocomplete-target-criteria'
      PaperComponent={React.forwardRef((props, ref) => (
        <Paper
          {...{
            ...props,
            ref,
          }}
          data-cy='autocomplete-target-criteria-options'
        />
      ))}
    />
  );
}
