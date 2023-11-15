import { InputAdornment } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useAllProgramsForChoicesLazyQuery } from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { useDebounce } from '../../hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleOptionSelected,
} from '../../utils/utils';
import TextField from '../TextField';
import { StyledAutocomplete } from './StyledAutocomplete';

export const ProgramAutocomplete = ({
  disabled,
  name,
  filter,
  value,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
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
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const history = useHistory();
  const location = useLocation();
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 1000);

  const [loadData, { data, loading }] = useAllProgramsForChoicesLazyQuery({
    variables: { businessArea, search: debouncedInputText },
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

  const allEdges = get(data, 'allPrograms.edges', []);

  return (
    <StyledAutocomplete
      value={value}
      icon={<FlashOnIcon />}
      data-cy='filters-program'
      open={open}
      filterOptions={(options) => options}
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
      onClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) =>
        handleOptionSelected(option.node?.id, value1)
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
          label={t('Programme')}
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position='start'>
                <FlashOnIcon />
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
