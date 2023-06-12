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
`;
export const SearchTextField = ({
  fullWidth = true,
  ...props
}): React.ReactElement => {
  return (
    <StyledTextField
      {...props}
      fullWidth={fullWidth}
      variant='outlined'
      margin='dense'
      inputProps={{ maxLength: 200 }}
      // https://github.com/mui-org/material-ui/issues/12805
      // eslint-disable-next-line react/jsx-no-duplicate-props
      InputProps={{
        startAdornment: (
          <InputAdornment position='start'>
            <SearchIcon />
          </InputAdornment>
        ),
      }}
    />
  );
};
