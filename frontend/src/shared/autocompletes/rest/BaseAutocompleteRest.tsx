import * as React from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { StyledAutocomplete, StyledTextField } from '../StyledAutocomplete';

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
  handleClose,
  handleOptionSelected,
  handleOptionLabel,
  handleOpen,
  open,
  inputValue,
  onInputTextChange,
  debouncedInputText,
  startAdornment = null,
  options = [],
  mapOptions = (opts) => opts,
  autocompleteProps = {},
  textFieldProps = {},
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  handleClose: (_: any, reason: string) => void;
  handleOptionSelected: (option: OptionType, value: OptionType) => boolean;
  handleOptionLabel: (option: OptionType) => string;
  handleOpen: () => void;
  open: boolean;
  inputValue: string;
  onInputTextChange: (value) => void;
  debouncedInputText: string;
  startAdornment?: React.ReactNode;
  options?: OptionType[];
  mapOptions?: (options: OptionType[]) => OptionType[];
  autocompleteProps?: Record<string, any>;
  textFieldProps?: Record<string, any>;
}): React.ReactElement {
  const prevValueRef = useRef(value);

  const { data, isLoading } = useQuery({
    queryKey: [label, businessArea, programId, queryParams],
    queryFn: () => fetchFunction(businessArea, programId, queryParams),
  });

  useEffect(() => {
    const prevValue = prevValueRef.current;
    if (prevValue !== '' && value === '' && inputValue !== '') {
      onInputTextChange('');
    }
    prevValueRef.current = value;
  }, [value, onInputTextChange, inputValue]);

  // load data on mount to match the value from the url
  useEffect(() => {
    if (open) {
      fetchFunction(businessArea, programId, queryParams);
    }
  }, [
    open,
    debouncedInputText,
    fetchFunction,
    businessArea,
    programId,
    queryParams,
  ]);

  if (!data) return null;

  const modifiedOptions = mapOptions(
    options.length > 0 ? options : data.results || [],
  );

  return (
    <StyledAutocomplete
      key={prevValueRef.current}
      freeSolo={false}
      filterOptions={(x) => x}
      value={value}
      data-cy={dataCy}
      open={open}
      options={modifiedOptions}
      onChange={handleChange}
      onOpen={handleOpen}
      onClose={handleClose}
      isOptionEqualToValue={(option, selectedValue) =>
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
        handleOptionSelected(option as any, selectedValue as any)
      }
      getOptionLabel={handleOptionLabel}
      disabled={disabled}
      loading={isLoading}
      {...autocompleteProps}
      renderInput={(params) => (
        <StyledTextField
          {...params}
          label={label}
          variant="outlined"
          size="small"
          data-cy={`${label}-input`}
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
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
          }}
          {...textFieldProps}
        />
      )}
    />
  );
}
