import get from 'lodash/get';
import * as React from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAllUsersForFiltersLazyQuery } from '@generated/graphql';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { useDebounce } from '@hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleAutocompleteClose,
  handleOptionSelected,
} from '@utils/utils';
import { BaseAutocomplete } from './BaseAutocomplete';

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
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
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

  const isMounted = useRef(true);

  const loadDataCallback = useCallback(() => {
    const asyncLoadData = async () => {
      if (isMounted.current && businessArea) {
        try {
          await loadData({
            variables: { businessArea, search: debouncedInputText },
          });
        } catch (error) {
          console.error(error);
        }
      }
    };

    void asyncLoadData();
  }, [loadData, businessArea, debouncedInputText]);

  useEffect(() => {
    if (open) {
      loadDataCallback();
    }
    return () => {
      isMounted.current = false;
    };
  }, [open, debouncedInputText, loadDataCallback]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    navigate,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const allEdges = get(data, 'allUsers.edges', []);

  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={label || t('Created By')}
      dataCy="filters-created-by-autocomplete"
      loadData={loadData}
      loading={loading}
      allEdges={allEdges}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
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
        getAutocompleteOptionLabel(option, allEdges, inputValue, 'individual')
      }
      data={data}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
};
