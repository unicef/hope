import { TextField } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../hooks/useBusinessArea';
import { useDebounce } from '../hooks/useDebounce';
import { useAllProgramsForChoicesLazyQuery } from '../__generated__/graphql';

const StyledAutocomplete = styled(Autocomplete)`
  && {
    width: ${({ theme }) => theme.spacing(58)}px;
    color: #e3e6e7;
  }

  .MuiAutocomplete-inputRoot {
    background-color: #465861;
    margin-bottom: 3px;
    color: #e3e6e7;
    border-bottom-width: 0;
    border-radius: 4px;
    height: 42px;
  }

  .MuiFormLabel-root {
    color: #e3e6e7;
  }
  .MuiIconButton-label {
    color: #e3e6e7;
  }
`;

export const GlobalProgramAutocomplete = ({
  disabled,
  fullWidth,
  onFilterChange,
  name,
  value,
  label,
}: {
  disabled?;
  fullWidth?: boolean;
  onFilterChange?;
  name?;
  value?;
  label?;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const businessArea = useBusinessArea();

  const [loadData, { data, loading }] = useAllProgramsForChoicesLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'name',
      search: debouncedInputText,
    },
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  const onChangeMiddleware = (e, selectedValue): void => {
    onFilterChange((filters) => ({
      ...filters,
      [name]: selectedValue?.node?.id || undefined,
    }));
  };
  return (
    <StyledAutocomplete
      value={value}
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChangeMiddleware}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => {
        return value1?.node?.id === option.node.id;
      }}
      getOptionLabel={(option) => option.node.name}
      disabled={disabled}
      options={get(data, 'allPrograms.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label || t('Programme')}
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
