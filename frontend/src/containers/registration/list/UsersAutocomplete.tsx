import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { InputAdornment } from '@material-ui/core';
import PersonIcon from '@material-ui/icons/Person';
import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import {
  AllUsersQuery,
  useAllUsersQuery,
} from '../../../__generated__/graphql';
import { useDebounce } from '../../../hooks/useDebounce';
import TextField from '../../../shared/TextField';

const StyledAutocomplete = styled(Autocomplete)`
  width: 232px;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function UsersAutocomplete({
  value,
  onChange,
  onInputTextChange,
  inputValue,
}): React.ReactElement {
  const [open, setOpen] = React.useState(false);
  const debouncedInputText = useDebounce(inputValue, 500);
  const [newValue, setNewValue] = useState();
  const { data, loading } = useAllUsersQuery({
    variables: {
      first: 100,
      fullName: debouncedInputText,
    },
  });
  useEffect(() => setNewValue(value), [data, value]);
  return (
    <StyledAutocomplete<AllUsersQuery['allUsers']['edges'][number]>
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChange}
      value={newValue}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      getOptionSelected={(option, value1) => {
        return value1 === option.node.id;
      }}
      getOptionLabel={(option) => {
        if (!option.node) {
          return '';
        }
        return `${option.node.firstName} ${option.node.lastName}`;
      }}
      options={get(data, 'allUsers.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label='Imported By'
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position='start'>
                <PersonIcon style={{ color: '#5f6368' }} />
              </InputAdornment>
            ),
            endAdornment: (
              <>
                {loading ? (
                  <CircularProgress color='inherit' size={20} />
                ) : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
}
