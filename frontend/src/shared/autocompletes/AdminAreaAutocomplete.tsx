import { CircularProgress, InputAdornment, TextField } from '@material-ui/core';
import RoomRoundedIcon from '@material-ui/icons/RoomRounded';
import { get } from 'lodash';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  AllAdminAreasQuery,
  useAllAdminAreasLazyQuery,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { useDebounce } from '../../hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleAutocompleteClose,
  handleOptionSelected,
} from '../../utils/utils';
import { StyledAutocomplete } from './StyledAutocomplete';

export const AdminAreaAutocomplete = ({
  disabled,
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
  const { businessArea } = useBaseUrl();

  const [loadAdminAreas, { data, loading }] = useAllAdminAreasLazyQuery({
    variables: {
      first: 20,
      name: debouncedInputText,
      businessArea,
      level: 2,
    },
    fetchPolicy: 'cache-and-network',
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

  const allEdges = get(data, 'allAdminAreas.edges', []);

  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      value={value}
      data-cy={dataCy}
      open={open}
      filterOptions={(options1) => options1}
      onChange={(_, selectedValue) => {
        handleAutocompleteChange(
          name,
          selectedValue?.node?.id,
          handleFilterChange,
        );
      }}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(_, reason) =>
        handleAutocompleteClose(setOpen, onInputTextChange, reason)
      }
      getOptionSelected={(option, value1) =>
        handleOptionSelected(option?.node?.id, value1)
      }
      getOptionLabel={(option) =>
        getAutocompleteOptionLabel(option, allEdges, inputValue)
      }
      disabled={disabled}
      options={allEdges}
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
