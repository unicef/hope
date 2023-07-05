import { CircularProgress, InputAdornment, TextField } from '@material-ui/core';
import RoomRoundedIcon from '@material-ui/icons/RoomRounded';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { get } from 'lodash';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { createHandleApplyFilterChange } from '../../utils/utils';
import {
  AllAdminAreasQuery,
  useAllAdminAreasLazyQuery,
} from '../../__generated__/graphql';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const AdminAreaAutocomplete = ({
  disabled,
  fullWidth = true,
  name,
  filter,
  value,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  dataCy,
}: {
  disabled?: boolean;
  fullWidth?: boolean;
  name: string;
  filter;
  value: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
  dataCy?: string;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const history = useHistory();
  const location = useLocation();
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

  // load all admin areas on mount to match the value from the url
  useEffect(() => {
    loadAdminAreas();
  }, [loadAdminAreas]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  if (!data) return null;

  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      value={value}
      fullWidth={fullWidth}
      data-cy={dataCy}
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
        return option.node.id === value1;
      }}
      getOptionLabel={(option) => {
        let label;
        if (option.node) {
          label = `${option.node.name}`;
        } else {
          label =
            data?.allAdminAreas?.edges?.find((el) => el.node.id === option)
              ?.node.name || '';
        }
        return `${label}`;
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
};
