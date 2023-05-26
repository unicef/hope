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
  ...otherProps
}): React.ReactElement => {
  return (
    <StyledFormControl variant='outlined' margin='dense'>
      {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
      {/*@ts-ignore*/}
      <InputLabel>{label}</InputLabel>
      {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
      {/*@ts-ignore*/}
      <Select
        /* eslint-disable-next-line @typescript-eslint/ban-ts-comment */
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
        {...otherProps}
      >
        {children}
      </Select>
    </StyledFormControl>
  );
};
