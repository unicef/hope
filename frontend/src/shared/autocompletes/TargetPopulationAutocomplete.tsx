import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useAllTargetPopulationForChoicesLazyQuery } from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { useDebounce } from '../../hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleAutocompleteClose,
  handleOptionSelected,
} from '../../utils/utils';
import { BaseAutocomplete } from './BaseAutocomplete';

export const TargetPopulationAutocomplete = ({
  disabled,
  name,
  filter,
  value,
  label,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
}: {
  disabled?;
  fullWidth?: boolean;
  name: string;
  filter;
  value: string;
  label?: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { businessArea, programId } = useBaseUrl();

  const [
    loadData,
    { data, loading },
  ] = useAllTargetPopulationForChoicesLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'name',
      name: debouncedInputText,
      program: [programId],
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  // load all TPs on mount to match the value from the url
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

  const allEdges = get(data, 'allTargetPopulations.edges', []);

  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={label || t('Target Population')}
      dataCy='filters-target-population-autocomplete'
      loadData={loadData}
      loading={loading}
      allEdges={allEdges}
      handleChange={(_, selectedValue) => {
        handleAutocompleteChange(
          name,
          selectedValue?.node?.id,
          handleFilterChange,
        );
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) =>
        handleAutocompleteClose(setOpen, onInputTextChange, reason)
      }
      handleOptionSelected={(option, value1) =>
        handleOptionSelected(option?.node?.id, value1)
      }
      handleOptionLabel={(option) =>
        getAutocompleteOptionLabel(option, allEdges, inputValue)
      }
      data={data}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
};
