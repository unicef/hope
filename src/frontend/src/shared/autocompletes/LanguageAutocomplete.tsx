import * as React from 'react';
import get from 'lodash/get';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useLanguageAutocompleteLazyQuery } from '@generated/graphql';
import { useDebounce } from '@hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleOptionSelected,
} from '@utils/utils';
import { BaseAutocomplete } from './BaseAutocomplete';

export function LanguageAutocomplete({
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
}): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  const [loadData, { data, loading }] = useLanguageAutocompleteLazyQuery({
    variables: {
      first: 20,
      code: debouncedInputText,
    },
    fetchPolicy: 'cache-and-network',
  });

  const isMounted = useRef(true);

  const loadDataCallback = useCallback(() => {
    const asyncLoadData = async () => {
      if (isMounted.current) {
        try {
          await loadData({ variables: { code: debouncedInputText } });
        } catch (error) {
          console.error(error);
        }
      }
    };

    void asyncLoadData();
  }, [loadData, debouncedInputText]);

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

  const allEdges = get(data, 'allLanguages.edges', []);

  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={t('Preferred language')}
      dataCy={dataCy}
      loadData={loadData}
      loading={loading}
      allEdges={allEdges}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
        handleAutocompleteChange(
          name,
          selectedValue?.node?.code,
          handleFilterChange,
        );
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      handleOptionSelected={(option, value1) =>
        handleOptionSelected(option?.node?.code, value1)
      }
      handleOptionLabel={(option) =>
        getAutocompleteOptionLabel(option, allEdges, inputValue, 'language')
      }
      data={data}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
}
