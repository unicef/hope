import { Autocomplete, TextField } from '@mui/material';
import styled from 'styled-components';

export const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
  .MuiAutocomplete-tag {
    max-height: 50px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .MuiAutocomplete-inputRoot {
    display: flex;
    flex-wrap: nowrap;
  }
  .MuiAutocomplete-inputRoot .MuiAutocomplete-input {
    flex-grow: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
`;

export const StyledTextField = styled(TextField)`
  & .MuiInputBase-input {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
`;
