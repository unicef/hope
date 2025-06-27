import { Autocomplete, Box, TextField, CircularProgress } from '@mui/material';
import  { useState, useEffect, ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useAllAdminAreasQuery } from '@generated/graphql';
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
  const { data, loading, error } = useAllAdminAreasQuery({
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

  const handleOnChange = (event, selectedValue, reason): void => {
    setInputValue(selectedValue?.node?.name);
    onChange(event, selectedValue, reason);
    if (additionalOnChange) {
      additionalOnChange();
    }
    if (reason === 'clear' && onClear) {
      onClear();
    }
  };

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <Box mt={1}>
      <StyledAutocomplete
        options={data?.allAdminAreas.edges || []}
        defaultValue={
          data && typeof value === 'string'
            ? data.allAdminAreas.edges.find((item) => item.node.id === value)
            : value
        }
        getOptionLabel={(option: any) =>
          option.node ? `${option.node.name}` : ''
        }
        // eslint-disable-next-line
        isOptionEqualToValue={(option: any, value: any) =>
          typeof value === 'string'
            ? option?.node?.id === value
            : option?.node?.id === value?.node?.id
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
