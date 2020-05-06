import React, { useState, useEffect } from 'react';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { TextField } from '@material-ui/core';
import styled from 'styled-components';

const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
`
interface Option {
  labelEn: string;
}

export function CriteriaAutocomplete({
  field,
  form,
  ...otherProps
}): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [newValue, setNewValue] = useState();
  useEffect(() => { 
    const optionValue = otherProps.choices.find(choice => choice.name === field.value) || null;
    setNewValue(optionValue)
  }, [field.value, otherProps.choices]);
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
          if(option) {
            return option.labelEn
          }
          return '';
        }
      }
      renderInput={(params) => (
        <TextField
          {...params}
          {...otherProps}
          variant='outlined'
          margin='dense'
          fullWidth
          InputProps={{
            ...params.InputProps,
          }}
        />
      )}
    />
  );
}
