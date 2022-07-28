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
  fullWidth = false,
  borderRadius = '4px',
  ...props
}): React.ReactElement => {
  return (
    <StyledTextField
      {...props}
      fullWidth={fullWidth}
      borderRadius={borderRadius}
      variant='outlined'
      margin='dense'
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
