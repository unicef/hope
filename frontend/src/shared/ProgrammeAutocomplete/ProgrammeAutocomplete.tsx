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

export function ProgrammeAutocomplete({
  field,
  form,
  ...otherProps
}): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [newValue, setNewValue] = useState(null);

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
      onChange={(e, object) => {
        if(object) {
          setNewValue(object)
          otherProps.onChange(e, object)
        }
      }}
      getOptionLabel={(option) => {
          if(option) {
            return option.name
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
