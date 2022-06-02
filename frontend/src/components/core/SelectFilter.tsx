import { InputLabel, Select } from '@material-ui/core';
import React from 'react';
import { StyledFormControl } from '../StyledFormControl';

export const SelectFilter = ({
  label,
  children,
  onChange,
  ...otherProps
}): React.ReactElement => {
  return (
    <StyledFormControl variant='outlined' margin='dense'>
      <InputLabel>{label}</InputLabel>
      <Select
        /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
        // @ts-ignore
        onChange={onChange}
        variant='outlined'
        label={label}
        {...otherProps}
      >
        {children}
      </Select>
    </StyledFormControl>
  );
};
