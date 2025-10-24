import { InputAdornment } from '@mui/material';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { BaseAutocompleteFilterRest } from '@shared/autocompletes/BaseAutocompleteFilterRest';

export function ProgramAutocompleteRestFilter({
  disabled,
  name,
  filter,
  value,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  dataCy = 'program-autocomplete',
}: {
  disabled?: boolean;
  name: string;
  filter?: any;
  value?: string;
  initialFilter: any;
  appliedFilter: any;
  setAppliedFilter: (filter: any) => void;
  setFilter: (filter: any) => void;
  dataCy?: string;
}): ReactElement {
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  const [queryVariables, setQueryVariables] = useState({
    limit: 20,
    businessAreaSlug: businessArea,
    search: debouncedInputText || undefined,
  });

  const {
    data: dataPrograms,
    isLoading,
    refetch,
  } = useQuery<PaginatedProgramListList>({
    queryKey: ['businessAreasProgramsList', queryVariables, businessArea],
    queryFn: () => RestService.restBusinessAreasProgramsList(queryVariables),
  });

  // Update query variables when search text changes
  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      search: debouncedInputText || undefined,
    }));
  }, [debouncedInputText]);

  const loadData = useCallback(() => {
    if (businessArea) {
      refetch();
    }
  }, [businessArea, refetch]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    navigate,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const programs = dataPrograms?.results || [];
  const options = programs.map((program) => ({
    id: program.id,
    name: program.name,
  }));

  const handleOptionSelected = (option: any, selectedValue: any) => {
    if (typeof selectedValue === 'string') {
      return option?.id === selectedValue;
    }
    return option?.id === selectedValue?.id;
  };

  const handleOptionLabel = (option: any) => {
    if (typeof option === 'string') {
      const matchingProgram = programs.find((program) => program.id === option);
      return matchingProgram?.name || option;
    }
    return option?.name || '';
  };

  const onInputTextChange = (v: string) => {
    setInputValue(v);
  };

  return (
    <BaseAutocompleteFilterRest
      value={value}
      disabled={disabled}
      label={t('Programme')}
      dataCy={dataCy}
      loadData={loadData}
      loading={isLoading}
      options={options}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
        handleAutocompleteChange(name, selectedValue?.id, handleFilterChange);
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      handleOptionSelected={handleOptionSelected}
      handleOptionLabel={handleOptionLabel}
      data={dataPrograms}
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
