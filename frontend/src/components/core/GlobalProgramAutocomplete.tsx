import { TextField } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import get from 'lodash/get';
import { useHistory } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useAllProgramsForChoicesLazyQuery } from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';

const StyledAutocomplete = styled(Autocomplete)`
  && {
    width: ${({ theme }) => theme.spacing(58)}px;
    color: #e3e6e7;
  }
  .MuiAutocomplete-inputRoot {
    background-color: #465861;
    margin-bottom: 5px;
    color: #e3e6e7;
    border-radius: 4px;
    height: 42px;
    padding: 0 10px;
  }
  .MuiAutocomplete-inputRoot:hover {
    background-color: #1d2c32;
  }
  .MuiFormLabel-root {
    color: #e3e6e7;
  }
  .MuiIconButton-label {
    color: #e3e6e7;
  }
  .MuiOutlinedInput-notchedOutline {
    border: none;
  }
`;

export const GlobalProgramAutocomplete = ({
  disabled,
  fullWidth,
  onFilterChange,
  name,
  value,
}: {
  disabled?;
  fullWidth?: boolean;
  onFilterChange;
  name?;
  value?;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const businessArea = useBusinessArea();
  const history = useHistory();

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

    if (selectedValue?.node?.id) {
      history.push(`/${businessArea}/${selectedValue?.node?.id}`);
    }
  };
  const programsOptions = [
    { node: { id: 'all', name: 'All' } },
    ...get(data, 'allPrograms.edges', []),
  ];
  return (
    <StyledAutocomplete
      value={value}
      defaultValue={{ node: { id: 'all', name: 'All' } }}
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
      options={programsOptions}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder={t('Programme')}
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
