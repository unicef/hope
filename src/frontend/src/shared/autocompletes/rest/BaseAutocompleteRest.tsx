import CircularProgress from '@mui/material/CircularProgress';
import { ReactElement, ReactNode, useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { StyledAutocomplete, StyledTextField } from '../StyledAutocomplete';
import { useDebounce } from '@hooks/useDebounce';
import { FormHelperText } from '@mui/material';

type OptionType = any;

export function BaseAutocompleteRest({
  value,
  disabled,
  label,
  dataCy,
  fetchFunction,
  businessArea,
  programId,
  queryParams,
  handleChange,
  handleOptionSelected,
  handleOptionLabel,
  startAdornment = null,
  mapOptions = (opts) => opts,
  autocompleteProps = {},
  textFieldProps = {},
  onDebouncedInputTextChanges,
  required = false,
  error = null,
}: {
  value: string;
  disabled?: boolean;
  label: string;
  dataCy?: string;
  fetchFunction: (
    businessArea: string,
    programId: string,
    queryParams?: Record<string, any>,
  ) => Promise<any>;
  businessArea: string;
  programId: string;
  queryParams?: Record<string, any>;
  handleChange: (event, newValue) => void;
  handleOptionSelected: (option: OptionType, value: OptionType) => boolean;
  handleOptionLabel: (option: OptionType) => string;
  startAdornment?: ReactNode;
  mapOptions?: (options: OptionType[]) => OptionType[];
  autocompleteProps?: Record<string, any>;
  textFieldProps?: Record<string, any>;
  onDebouncedInputTextChanges: (text: string) => void;
  required?: boolean;
  error?: string;
}): ReactElement {
  const [modifiedOptions, setModifiedOptions] = useState<OptionType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const [open, setOpen] = useState(false);
  const { data, isLoading } = useQuery({
    queryKey: [label, businessArea, programId, queryParams],
    queryFn: () => fetchFunction(businessArea, programId, { ...queryParams }),
  });
  useEffect(
    () => onDebouncedInputTextChanges(debouncedInputText),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [debouncedInputText],
  );

  useEffect(() => {
    if (value === '' && inputValue !== '') {
      setInputValue('');
    }
  }, [value, setInputValue, inputValue]);

  useEffect(() => {
    setModifiedOptions(mapOptions(data?.results || []));
  }, [data, mapOptions]);

  return (
    <StyledAutocomplete
      freeSolo={false}
      filterOptions={(x) => x}
      value={value}
      data-cy={dataCy}
      open={open}
      options={modifiedOptions}
      onChange={handleChange}
      onOpen={() => setOpen(true)}
      onClose={() => {
        setOpen(false);
        if (value === null) {
          setInputValue('');
        }
      }}
      isOptionEqualToValue={(option, selectedValue) =>
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
        handleOptionSelected(option as any, selectedValue as any)
      }
      getOptionLabel={handleOptionLabel}
      disabled={disabled}
      loading={isLoading}
      {...autocompleteProps}
      renderInput={(params) => (
        <>
          <StyledTextField
            {...params}
            label={label}
            required={required}
            error={!!error}
            aria-errormessage={error}
            variant="outlined"
            size="small"
            data-cy={`${label}-input`}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            slotProps={{
              input: {
                ...params.InputProps,
                startAdornment,
                endAdornment: (
                  <>
                    {isLoading ? (
                      <CircularProgress color="inherit" size={20} />
                    ) : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              },
            }}
            {...textFieldProps}
          />
          {!!error && <FormHelperText error>{error}</FormHelperText>}
        </>
      )}
    />
  );
}
