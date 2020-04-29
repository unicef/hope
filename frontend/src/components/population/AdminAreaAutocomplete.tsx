import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { InputAdornment } from '@material-ui/core';
import RoomRoundedIcon from '@material-ui/icons/RoomRounded';
import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { useDebounce } from '../../hooks/useDebounce';
import TextField from '../../shared/TextField';
import {
  AllAdminAreasQuery,
  useAllAdminAreasQuery,
} from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const StyledAutocomplete = styled(Autocomplete)`
  width: 232px;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function AdminAreasAutocomplete({ value, onChange }) {
  const [open, setOpen] = React.useState(false);
  const [inputValue, onInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 500);
  const [newValue, setNewValue] = useState();
  const businessArea = useBusinessArea();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      title: debouncedInputText,
      businessArea,
    },
  });
  useEffect(() => setNewValue(value), [data, value]);
  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
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
        return `${option.node.title}`;
      }}
      options={get(data, 'allAdminAreas.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label='Location'
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position='start'>
                <RoomRoundedIcon style={{ color: '#5f6368' }} />
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
