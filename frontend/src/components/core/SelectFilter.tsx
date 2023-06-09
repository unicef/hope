import { InputAdornment } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import { StyledFormControl } from '../StyledFormControl';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

export const SelectFilter = ({
  label,
  children,
  onChange,
  icon = null,
  fullWidth = true,
  ...otherProps
}): React.ReactElement => {
  return (
    <StyledFormControl fullWidth={fullWidth} variant='outlined' margin='dense'>
      <InputLabel>{label}</InputLabel>
      <Select
        /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
        // @ts-ignore
        onChange={onChange}
        variant='outlined'
        label={label}
        InputProps={
          icon
            ? {
                startAdornment: (
                  <StartInputAdornment position='start'>
                    {icon}
                  </StartInputAdornment>
                ),
              }
            : null
        }
        fullWidth={fullWidth}
        {...otherProps}
      >
        {children}
      </Select>
    </StyledFormControl>
  );
};
