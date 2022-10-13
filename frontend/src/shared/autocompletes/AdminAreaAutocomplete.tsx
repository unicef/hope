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
  AreaNodeEdge,
  AllAdminAreasQuery,
  useAllAdminAreasLazyQuery,
} from '../../__generated__/graphql';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function AdminAreaAutocomplete({
  disabled,
  fullWidth,
  onFilterChange,
  name,
  value,
}: {
  disabled?;
  fullWidth?: boolean;
  onFilterChange;
  name: string;
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

  const onChangeMiddleware = (e, selectedValue): void => {
    onFilterChange((filters) => ({
      ...filters,
      [name]: selectedValue || undefined,
    }));
  };
  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      value={value}
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChangeMiddleware}
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
