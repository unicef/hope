import { InputAdornment } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import styled from 'styled-components';
import React from 'react';
import TextField from '../../shared/TextField';

const StyledTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
  .MuiOutlinedInput-root {
    border-radius: ${(props) => props.borderRadius};
  }
`;
export const SearchTextField = ({
  icon = null,
  borderRadius = '4px',
  fullWidth = true,
  ...props
}): React.ReactElement => {
  return (
    <StyledTextField
      {...props}
      fullWidth={fullWidth}
      borderRadius={borderRadius}
      variant='outlined'
      margin='dense'
      inputProps={{ maxLength: 200 }}
      // https://github.com/mui-org/material-ui/issues/12805
      // eslint-disable-next-line react/jsx-no-duplicate-props
      InputProps={{
        startAdornment: (
          <InputAdornment position='start'>
            {(icon as JSX.Element) || <SearchIcon />}
          </InputAdornment>
        ),
      }}
    />
  );
};
