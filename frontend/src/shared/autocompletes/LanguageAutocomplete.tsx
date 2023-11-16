import CircularProgress from '@material-ui/core/CircularProgress';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useLanguageAutocompleteLazyQuery } from '../../__generated__/graphql';
import { useDebounce } from '../../hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleOptionSelected,
} from '../../utils/utils';
import TextField from '../TextField';
import { StyledAutocomplete } from './StyledAutocomplete';

export const LanguageAutocomplete = ({
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
  disabled?;
  name: string;
  filter?;
  value?: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
  dataCy?: string;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const history = useHistory();
  const location = useLocation();
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 1000);

  const [loadData, { data, loading }] = useLanguageAutocompleteLazyQuery({
    variables: {
      first: 20,
      code: debouncedInputText,
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  // load all languages on mount to match the value from the url
  useEffect(() => {
    loadData();
  }, [loadData]);

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

  const allEdges = get(data, 'allLanguages.edges', []);

  return (
    <StyledAutocomplete
      value={value}
      data-cy={dataCy}
      open={open}
      filterOptions={(options) => options}
      onChange={(_, selectedValue) => {
        handleAutocompleteChange(
          name,
          selectedValue?.node?.code,
          handleFilterChange,
        );
      }}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) =>
        handleOptionSelected(option.node?.code, value1)
      }
      getOptionLabel={(option) =>
        getAutocompleteOptionLabel(option, allEdges, inputValue, 'language')
      }
      disabled={disabled}
      options={allEdges}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={t('Preferred language')}
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
