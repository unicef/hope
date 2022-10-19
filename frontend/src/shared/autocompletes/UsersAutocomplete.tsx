import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { InputAdornment } from '@material-ui/core';
import PersonIcon from '@material-ui/icons/Person';
import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import {
  AllUsersQuery,
  useAllUsersForFiltersLazyQuery,
} from '../../__generated__/graphql';
import { useDebounce } from '../../hooks/useDebounce';
import TextField from '../TextField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { renderUserName } from '../../utils/utils';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => props.fullWidth || '232px'};
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const UsersAutocomplete = ({
  value,
  onChange,
  onInputTextChange,
  inputValue,
  fullWidth = false,
}): React.ReactElement => {
  const [open, setOpen] = React.useState(false);
  const businessArea = useBusinessArea();
  const debouncedInputText = useDebounce(inputValue, 500);
  const [newValue, setNewValue] = useState();

  const [loadData, { data, loading }] = useAllUsersForFiltersLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'first_name,last_name,email',
      search: debouncedInputText,
    },
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  useEffect(() => setNewValue(value), [data, value]);

  return (
    <StyledAutocomplete<AllUsersQuery['allUsers']['edges'][number]>
      fullWidth={fullWidth}
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
        return renderUserName(option.node);
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
};
