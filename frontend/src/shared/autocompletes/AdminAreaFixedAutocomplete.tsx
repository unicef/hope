import Autocomplete from '@mui/lab/Autocomplete';
import * as React from 'react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { CircularProgress, TextField } from '@mui/material';
import { useDebounce } from '@hooks/useDebounce';
import { AllAdminAreasQuery, useAllAdminAreasQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

const StyledAutocomplete = styled(Autocomplete)`
  .MuiFormControl-marginDense {
    //margin-top: 4px;
  }
`;

export function AdminAreaFixedAutocomplete({
  value,
  onChange,
  disabled,
  level,
  parentId,
  onClear,
  additionalOnChange,
  dataCy,
}: {
  value: string | AllAdminAreasQuery['allAdminAreas']['edges'][number]['node'];
  onChange;
  disabled?;
  level?;
  parentId?;
  onClear?: () => void;
  additionalOnChange?: () => void;
  dataCy?: string;
}): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = React.useState(false);
  const [inputValue, onInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 800);
  const [newValue, setNewValue] = useState(null);
  const { businessArea } = useBaseUrl();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      name: debouncedInputText,
      businessArea,
      first: 50,
      level: level === 1 ? 1 : 2,
      parentId: parentId || '',
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    if (data) {
      setNewValue(
        typeof value === 'string'
          ? data.allAdminAreas.edges.find((item) => item.node.name === value)
          : value,
      );
    }
  }, [data, value]);

  const onChangeMiddleware = (e, selectedValue, reason): void => {
    onInputTextChange(selectedValue?.node?.name);
    onChange(e, selectedValue, reason);
    if (additionalOnChange) {
      additionalOnChange();
    }
    if (reason === 'clear' && onClear) {
      onClear();
    }
  };

  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChangeMiddleware}
      value={newValue}
      data-cy={dataCy || 'admin-area-autocomplete'}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (value || reason === 'select-option') return;
        onInputTextChange(null);
      }}
      isOptionEqualToValue={(option, selectedValue) =>
        selectedValue?.node?.id === option.node.id
      }
      getOptionLabel={(option) => {
        if (!option.node) {
          return '';
        }
        return `${option.node.name}`;
      }}
      disabled={disabled}
      options={get(data, 'allAdminAreas.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={
            level === 1
              ? t('Administrative Level 1')
              : t('Administrative Level 2')
          }
          variant="outlined"
          margin="dense"
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? (
                  <CircularProgress color="inherit" size={20} />
                ) : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
}
