import { Autocomplete, TextField } from '@mui/material';
import styled from 'styled-components';

export const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const StyledTextField = styled(TextField)`
  & .MuiInputBase-input {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
`;
