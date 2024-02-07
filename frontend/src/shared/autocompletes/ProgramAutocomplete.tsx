import { InputAdornment } from '@mui/material';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import get from 'lodash/get';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAllProgramsForChoicesLazyQuery } from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { useDebounce } from '../../hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  getAutocompleteOptionLabel,
  handleAutocompleteChange,
  handleOptionSelected,
} from '@utils/utils';
import { BaseAutocomplete } from './BaseAutocomplete';

export function ProgramAutocomplete({
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
}): React.ReactElement {
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  const [loadData, { data, loading }] = useAllProgramsForChoicesLazyQuery({
    variables: { businessArea, search: debouncedInputText },
    fetchPolicy: 'cache-and-network',
  });

  const isMounted = useRef(true);

  const loadDataCallback = useCallback(() => {
    if (businessArea) {
      loadData({ variables: { businessArea, search: debouncedInputText } });
    }
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

  const allEdges = get(data, 'allPrograms.edges', []);

  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={t('Programme')}
      dataCy="filters-program"
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
      handleClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
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
      startAdornment={
        <InputAdornment position="start">
          <FlashOnIcon />
        </InputAdornment>
      }
    />
  );
}
