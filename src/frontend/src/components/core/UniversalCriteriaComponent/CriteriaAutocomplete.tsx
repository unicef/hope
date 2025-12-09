import React, { useState, useEffect } from 'react';
import get from 'lodash/get';
import { Autocomplete, TextField, Paper } from '@mui/material';
import styled from 'styled-components';

const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
`;

export function CriteriaAutocomplete({
  field,
  choices,
  ...otherProps
}): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [newValue, setNewValue] = useState<any>(null);
  useEffect(() => {
    const optionValue =
      choices.find((choice: any) => choice.name === field.value) || null;
    setNewValue(optionValue);
  }, [field.value, choices]);

  const isInvalid =
    get(otherProps.form.errors, field.name) &&
    get(otherProps.form.touched, field.name);
  return (
    <StyledAutocomplete<any>
      {...field}
      {...otherProps}
      open={open}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      options={choices}
      value={newValue}
      getOptionLabel={(option: any) => {
        if (option) {
          return option.labelEn || '';
        }
        return '';
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          {...otherProps}
          variant="outlined"
          margin="dense"
          fullWidth
          helperText={isInvalid && get(otherProps.form.errors, field.name)}
          error={isInvalid}
          InputProps={{
            ...params.InputProps,
          }}
          slotProps={{
            htmlInput: {
              ...params.inputProps,
              'data-cy': `autocomplete-target-criteria-option-${otherProps.index}`,
            },
          }}
        />
      )}
      data-cy="autocomplete-target-criteria"
      PaperComponent={CriteriaAutocompletePaper}
    />
  );
}

const CriteriaAutocompletePaper = React.forwardRef<HTMLDivElement, any>(
  (props, ref) => (
    <Paper
      {...props}
      ref={ref}
      data-cy="autocomplete-target-criteria-options"
    />
  ),
);

CriteriaAutocompletePaper.displayName = 'CriteriaAutocompletePaper';
