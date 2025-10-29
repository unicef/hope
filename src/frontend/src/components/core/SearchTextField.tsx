import {
  InputAdornment,
  TextField,
  OutlinedTextFieldProps,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import styled from 'styled-components';
import React, { ReactElement } from 'react';

interface StyledTextFieldProps extends OutlinedTextFieldProps {
  $borderRadius?: string;
}

const StyledTextField = styled(TextField)<StyledTextFieldProps>`
  flex: 1;
  && {
    min-width: 150px;
  }
  .MuiOutlinedInput-root {
    border-radius: ${(props) => props.$borderRadius};
  }
`;

export function SearchTextField({
  icon = null,
  borderRadius = '4px',
  fullWidth = true,
  placeholder = 'Search',
  ...props
}): ReactElement {
  return (
    <StyledTextField
      {...props}
      size="small"
      fullWidth={fullWidth}
      $borderRadius={borderRadius}
      variant="outlined"
      placeholder={placeholder}
      inputProps={{ maxLength: 200 }}
      // https://github.com/mui-org/material-ui/issues/12805
       
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            {(icon as React.JSX.Element) || <SearchIcon />}
          </InputAdornment>
        ),
      }}
    />
  );
}
