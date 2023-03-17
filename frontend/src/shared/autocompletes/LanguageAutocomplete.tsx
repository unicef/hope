import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LocationState, useHistory, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useDebounce } from '../../hooks/useDebounce';
import { createHandleFilterChange } from '../../utils/utils';
import { useLanguageAutocompleteLazyQuery } from '../../__generated__/graphql';
import TextField from '../TextField';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const LanguageAutocomplete = ({
  disabled,
  fullWidth,
  name,
  onFilterChange,
  filter,
  value,
}: {
  disabled?;
  fullWidth?: boolean;
  name: string;
  onFilterChange: (filters: { [key: string]: string }) => void;
  filter?;
  value?: string;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);

  const [loadData, { data, loading }] = useLanguageAutocompleteLazyQuery({
    variables: {
      first: 20,
      code: debouncedInputText,
    },
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  // load all languages on mount to match the value from the url
  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    useHistory<LocationState>(),
    useLocation(),
  );

  if (!data) return null;

  return (
    <StyledAutocomplete
      value={value}
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options) => options}
      onChange={(_, selectedValue) =>
        handleFilterChange(name, selectedValue?.node?.code)
      }
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, v) => {
        return v === option.node.code;
      }}
      getOptionLabel={(option) => {
        let label;
        if (option.node) {
          label = `${option.node.english}`;
        } else {
          label =
            data?.allLanguages?.edges?.find((el) => el.node.code === option)
              ?.node.english || '';
        }
        return `${label}`;
      }}
      disabled={disabled}
      options={get(data, 'allLanguages.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={t('Preferred language')}
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
