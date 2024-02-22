import {
  InputAdornment,
  TextField,
  OutlinedTextFieldProps,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import styled from 'styled-components';
import * as React from 'react';

interface StyledTextFieldProps extends OutlinedTextFieldProps {
  borderRadius?: string;
}

const StyledTextField = styled(TextField)<StyledTextFieldProps>`
  flex: 1;
  && {
    min-width: 150px;
  }
  .MuiOutlinedInput-root {
    border-radius: ${(props) => props.borderRadius};
  }
`;

export function SearchTextField({
  icon = null,
  borderRadius = '4px',
  fullWidth = true,
  ...props
}): React.ReactElement {
  return (
    <StyledTextField
      {...props}
      size="medium"
      fullWidth={fullWidth}
      borderRadius={borderRadius}
      variant="outlined"
      margin="dense"
      inputProps={{ maxLength: 200 }}
      // https://github.com/mui-org/material-ui/issues/12805
      // eslint-disable-next-line react/jsx-no-duplicate-props
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            {(icon as JSX.Element) || <SearchIcon />}
          </InputAdornment>
        ),
      }}
    />
  );
}
