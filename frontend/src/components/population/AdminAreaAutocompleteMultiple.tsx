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
import { LoadingComponent } from '../LoadingComponent';

const StyledAutocomplete = styled(Autocomplete)`
  width: 232px;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function AdminAreaAutocompleteMultiple({
  value,
  onChange,
  disabled,
}: {
  value;
  onChange;
  disabled?;
}): React.ReactElement {
  const [open, setOpen] = React.useState(false);
  const [inputValue, setInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 500);
  const [newValue, setNewValue] = useState([]);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      title: debouncedInputText,
      businessArea,
    },
  });
  useEffect(() => {
    setNewValue(value);
  }, [data, value]);
  useEffect(() => {
    setInputTextChange('');
  }, [value]);

  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      open={open}
      multiple
      fullWidth
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
        return value1?.node?.id === option.node.id;
      }}
      getOptionLabel={(option) => {
        if (!option.node) {
          return '';
        }
        return `${option.node.title}`;
      }}
      disabled={disabled}
      options={get(data, 'allAdminAreas.edges', [])}
      loading={loading}
      renderInput={(params) => {
        return (
          <TextField
            {...params}
            inputProps={{
              ...params.inputProps,
              value: inputValue,
            }}
            label='Administrative Level 2'
            variant='outlined'
            margin='dense'
            value={inputValue}
            onChange={(e) => setInputTextChange(e.target.value)}
          />
        );
      }}
    />
  );
}
