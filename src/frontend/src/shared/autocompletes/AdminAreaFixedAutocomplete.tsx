import { Autocomplete, Box, TextField, CircularProgress } from '@mui/material';
import { useState, useEffect, ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const AdminAreaFixedAutocomplete = ({
  value,
  onChange,
  disabled,
  level,
  parentId,
  onClear,
  additionalOnChange,
  dataCy,
}): ReactElement => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const [, setNewValue] = useState(null);
  const { businessArea } = useBaseUrl();
  const {
    data: areasData,
    isLoading,
    error,
  } = useQuery({
    queryKey: [
      'adminAreas',
      debouncedInputText,
      businessArea,
      level,
      parentId,
      value,
    ],
    queryFn: () =>
      RestService.restAreasList({
        id: value || undefined,
        search: debouncedInputText || '',
        areaTypeAreaLevel: level === 1 ? 1 : 2,
        parentId: parentId || undefined,
        limit: 50,
      }),
  });

  const loading = isLoading;

  useEffect(() => {
    if (areasData) {
      setNewValue(
        typeof value === 'string'
          ? areasData.results.find((item) => item.name === value)
          : value,
      );
    }
  }, [areasData, value]);

  const handleOnChange = (event, selectedValue, reason): void => {
    setInputValue(selectedValue?.name);
    onChange(event, selectedValue, reason);
    if (additionalOnChange) {
      additionalOnChange();
    }
    if (reason === 'clear' && onClear) {
      onClear();
    }
  };

  if (error) {
    return (
      <div>
        Error: {error instanceof Error ? error.message : 'An error occurred'}
      </div>
    );
  }

  return (
    <Box mt={1}>
      <StyledAutocomplete
        options={areasData?.results || []}
        defaultValue={
          areasData && typeof value === 'string'
            ? areasData.results.find((item) => item.id === value)
            : value
        }
        getOptionLabel={(option: any) => (option ? `${option.name}` : '')}
        // eslint-disable-next-line
        isOptionEqualToValue={(option: any, value: any) =>
          typeof value === 'string'
            ? option?.id === value
            : option?.id === value?.id
        }
        onChange={handleOnChange}
        disabled={disabled}
        fullWidth
        renderInput={(params) => (
          <TextField
            {...params}
            size="small"
            label={
              level === 1
                ? t('Administrative Level 1')
                : t('Administrative Level 2')
            }
            variant="outlined"
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
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
        data-cy={dataCy || 'admin-area-autocomplete'}
      />
    </Box>
  );
};
