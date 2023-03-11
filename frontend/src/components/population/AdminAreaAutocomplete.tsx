import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation, LocationState } from 'react-router-dom';
import { get } from 'lodash';
import styled from 'styled-components';
import { TextField, InputAdornment, CircularProgress } from '@material-ui/core';
import RoomRoundedIcon from '@material-ui/icons/RoomRounded';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { createHandleFilterChange } from '../../utils/utils';
import {
  AreaNodeEdge,
  useAllAdminAreasLazyQuery,
  AllAdminAreasQuery,
} from '../../__generated__/graphql';
import Autocomplete from '@material-ui/lab/Autocomplete';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function AdminAreaAutocomplete({
  disabled,
  fullWidth,
  name,
  onFilterChange,
  value,
}: {
  disabled?: boolean;
  fullWidth?: boolean;
  name: string;
  onFilterChange: (filters: { [key: string]: string }) => void;
  value?: AreaNodeEdge;
}): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const businessArea = useBusinessArea();

  const [loadAdminAreas, { data, loading }] = useAllAdminAreasLazyQuery({
    variables: {
      first: 20,
      name: debouncedInputText,
      businessArea,
      level: 2,
    },
  });

  useEffect(() => {
    if (open) {
      loadAdminAreas();
    }
  }, [open, debouncedInputText, loadAdminAreas]);

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    useHistory<LocationState>(),
    useLocation(),
  );

  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      value={value}
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options1) => options1}
      onChange={(_, selectedValue) =>
        handleFilterChange(name, selectedValue?.node?.id)
      }
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => {
        return value1?.node?.id === option.node.id;
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
          label={t('Admin Level 2')}
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
