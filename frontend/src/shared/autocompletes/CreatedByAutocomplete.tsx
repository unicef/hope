import CircularProgress from '@material-ui/core/CircularProgress';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useAllUsersForFiltersLazyQuery } from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleAutocompleteClose,
  handleOptionSelected,
} from '../../utils/utils';
import TextField from '../TextField';
import { StyledAutocomplete } from './StyledAutocomplete';

export const CreatedByAutocomplete = ({
  disabled,
  name,
  filter,
  value,
  label,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  additionalVariables,
}: {
  disabled?: boolean;
  name: string;
  filter;
  value: string;
  label?: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
  additionalVariables;
}): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 1000);
  const businessArea = useBusinessArea();

  const [loadData, { data, loading }] = useAllUsersForFiltersLazyQuery({
    variables: {
      businessArea,
      first: 100,
      orderBy: 'first_name,last_name,email',
      search: debouncedInputText,
      ...additionalVariables,
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  // load all users on mount to match the value from the url
  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (!value) {
      onInputTextChange('');
    }
  }, [value, onInputTextChange]);

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

  const allEdges = get(data, 'allUsers.edges', []);

  return (
    <StyledAutocomplete
      value={value}
      data-cy='filters-created-by-autocomplete'
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
        getAutocompleteOptionLabel(option, allEdges, inputValue, 'individual')
      }
      disabled={disabled}
      options={allEdges}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          data-cy='filters-created-by-input'
          label={label || t('Created By')}
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
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
