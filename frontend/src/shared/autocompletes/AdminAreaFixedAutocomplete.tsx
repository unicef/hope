import { InputAdornment } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import RoomRoundedIcon from '@material-ui/icons/RoomRounded';
import Autocomplete from '@material-ui/lab/Autocomplete';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import TextField from '../TextField';
import {
  AllAdminAreasQuery,
  useAllAdminAreasQuery,
} from '../../__generated__/graphql';

const StyledAutocomplete = styled(Autocomplete)`
  .MuiFormControl-marginDense {
    //margin-top: 4px;
  }
`;

export function AdminAreaFixedAutocomplete({
  value,
  onChange,
  disabled,
}: {
  value;
  onChange;
  disabled?;
}): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = React.useState(false);
  const [inputValue, onInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 500);
  const [newValue, setNewValue] = useState(null);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      name: debouncedInputText,
      businessArea,
      first: 50,
      level: 2,
    },
  });

  useEffect(() => {
    if (data) {
      setNewValue(
        typeof value === 'string'
          ? data.allAdminAreas.edges.find((item) => item.node.name === value)
          : value,
      );
    } else {
      // setNewValue(value);
    }
    // onInputTextChange('');
  }, [data, value]);
  const onChangeMiddleware = (e, selectedValue, reason): void => {
    onInputTextChange(selectedValue?.node?.name);
    onChange(e, selectedValue, reason);
  };
  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChangeMiddleware}
      value={newValue}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (value || reason === 'select-option') return;
        onInputTextChange(null);
      }}
      getOptionSelected={(option, selectedValue) => {
        return selectedValue?.node?.id === option.node.id;
      }}
      getOptionLabel={(option) => {
        if (!option.node) {
          return '';
        }
        return `${option.node.name}`;
      }}
      disabled={disabled}
      options={get(data, 'allAdminAreas.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={t('Administrative Level 2')}
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
