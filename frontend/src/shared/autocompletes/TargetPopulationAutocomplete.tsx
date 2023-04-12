import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { useHistory, useLocation } from 'react-router-dom';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { createHandleFilterChange } from '../../utils/utils';
import { useAllTargetPopulationForChoicesLazyQuery } from '../../__generated__/graphql';
import TextField from '../TextField';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 6px;
  }
`;

export const TargetPopulationAutocomplete = ({
  disabled,
  fullWidth,
  name,
  onFilterChange,
  filter,
  value,
  label,
}: {
  disabled?;
  fullWidth?: boolean;
  name: string;
  onFilterChange: (filters: { [key: string]: string }) => void;
  filter;
  value: string;
  label?: string;
}): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const businessArea = useBusinessArea();

  const [
    loadData,
    { data, loading },
  ] = useAllTargetPopulationForChoicesLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'name',
      name: debouncedInputText,
    },
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

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  if (!data) return null;

  return (
    <StyledAutocomplete
      value={value}
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options1) => options1}
      onChange={(_, selectedValue) =>
        handleFilterChange(name, selectedValue?.node?.id)
      }
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => {
        return option.node?.id === value1;
      }}
      getOptionLabel={(option) => {
        let optionLabel;
        if (option.node) {
          optionLabel = `${option.node.name}`;
        } else {
          optionLabel =
            data?.allTargetPopulation?.edges?.find(
              (el) => el.node.id === option,
            )?.node.name || '';
        }
        return `${optionLabel}`;
      }}
      disabled={disabled}
      options={get(data, 'allTargetPopulation.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label || t('Target Population')}
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
