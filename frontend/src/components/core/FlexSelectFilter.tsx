import { Box, InputAdornment } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

export const FlexSelectFilter = ({
  label,
  children,
  onChange,
  icon = null,
  ...otherProps
}): React.ReactElement => {
  return (
    <Box display='flex' flexDirection='column'>
      <FormControl variant='outlined' margin='dense'>
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
      </FormControl>
    </Box>
  );
};
