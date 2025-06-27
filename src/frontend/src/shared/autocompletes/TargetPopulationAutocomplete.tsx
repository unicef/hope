import get from 'lodash/get';
import { ReactElement, useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAllTargetPopulationForChoicesLazyQuery } from '@generated/graphql';
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

export function TargetPopulationAutocomplete({
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
}): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { businessArea, programId } = useBaseUrl();

  const [loadData, { data, loading }] =
    useAllTargetPopulationForChoicesLazyQuery({
      variables: {
        businessArea,
        first: 20,
        orderBy: 'name',
        name: debouncedInputText,
        program: programId,
        status: ['DRAFT'],
      },
      fetchPolicy: 'cache-and-network',
    });

  const isMounted = useRef(true);
  const loadDataCallback = useCallback(() => {
    const asyncLoadData = async () => {
      if (isMounted.current && businessArea) {
        try {
          await loadData({
            variables: {
              program: programId,
              businessArea,
              name: debouncedInputText,
            },
          });
        } catch (error) {
          console.error(error);
        }
      }
    };

    void asyncLoadData();
  }, [loadData, businessArea, programId, debouncedInputText]);

  useEffect(() => {
    isMounted.current = true;
    if (open && isMounted.current) {
      loadDataCallback();
    }
    return () => {
      isMounted.current = false;
    };
  }, [open, debouncedInputText, loadDataCallback]);

  useEffect(() => {
    isMounted.current = true;
    if (isMounted.current) {
      loadDataCallback();
    }
    return () => {
      isMounted.current = false;
    };
  }, [loadDataCallback]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    navigate,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const allEdges = get(data, 'allTargetPopulation.edges', []);
  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={label || t('Target Population')}
      dataCy="filters-target-population-autocomplete"
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
}
