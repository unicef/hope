import { Box, InputAdornment } from '@material-ui/core';
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
  borderRadius = '4px',
  fullWidth = false,
  ...otherProps
}): React.ReactElement => {
  return (
    <StyledFormControl
      borderRadius={borderRadius}
      fullWidth={fullWidth}
      variant='outlined'
      margin='dense'
    >
      <Box display='grid'>
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
          {...otherProps}
        >
          {children}
        </Select>
      </Box>
    </StyledFormControl>
  );
};
