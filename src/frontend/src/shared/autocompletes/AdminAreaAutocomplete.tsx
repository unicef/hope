import { ReactElement, useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleAutocompleteClose,
  handleOptionSelected,
} from '@utils/utils';
import { BaseAutocomplete } from './BaseAutocomplete';

export function AdminAreaAutocomplete({
  disabled,
  name,
  level,
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
  level: number;
  filter;
  value: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
  dataCy?: string;
}): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const navigate = useNavigate();
  const location = useLocation();
  const { businessArea } = useBaseUrl();

  const {
    data: areasData,
    isLoading: loading,
    refetch,
  } = useQuery({
    queryKey: ['adminAreas', debouncedInputText, businessArea, level, open],
    queryFn: () =>
      RestService.restAreasList({
        search: debouncedInputText,
        areaTypeAreaLevel: level,
        limit: 20,
      }),
    enabled: open && !!businessArea,
  });

  const isMounted = useRef(true);

  const loadData = useCallback(() => {
    if (isMounted.current && businessArea && open) {
      refetch();
    }
  }, [refetch, businessArea, open]);

  const loadDataCallback = useCallback(() => {
    if (isMounted.current && businessArea && open) {
      loadData();
    }
  }, [loadData, businessArea, open]);

  useEffect(() => {
    if (open) {
      loadDataCallback();
    }
    return () => {
      isMounted.current = false;
    };
  }, [open, loadDataCallback]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    navigate,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const allEdges = areasData?.results || [];

  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={t(`Admin Level ${level}`)}
      dataCy={dataCy}
      loadData={loadData}
      loading={loading}
      allEdges={allEdges}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
        handleAutocompleteChange(name, selectedValue?.id, handleFilterChange);
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) =>
        handleAutocompleteClose(setOpen, onInputTextChange, reason)
      }
      handleOptionSelected={(option, value1) =>
        handleOptionSelected(option?.id, value1)
      }
      handleOptionLabel={(option) =>
        getAutocompleteOptionLabel(option, allEdges, inputValue)
      }
      data={areasData}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
}
