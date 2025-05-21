import CircularProgress from '@mui/material/CircularProgress';
import { ReactElement, ReactNode, useEffect, useRef } from 'react';
import { StyledAutocomplete, StyledTextField } from './StyledAutocomplete';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type OptionType = any;

export function BaseAutocompleteFilterRest({
  value,
  disabled,
  label,
  dataCy,
  loadData,
  loading,
  options,
  handleChange,
  handleClose,
  handleOptionSelected,
  handleOptionLabel,
  handleOpen,
  open,
  data,
  inputValue,
  onInputTextChange,
  debouncedInputText,
  startAdornment = null,
}: {
  value: string;
  disabled?: boolean;
  label: string;
  dataCy?: string;
  loadData;
  loading: boolean;
  options;
  handleChange: (event, newValue) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  handleClose: (_: any, reason: string) => void;
  handleOptionSelected: (option: OptionType, value: OptionType) => boolean;
  handleOptionLabel: (option: OptionType) => string;
  handleOpen: () => void;
  open: boolean;
  data;
  inputValue: string;
  onInputTextChange: (value) => void;
  debouncedInputText: string;
  startAdornment?: ReactNode;
}): ReactElement {
  const prevValueRef = useRef(value);

  useEffect(() => {
    const prevValue = prevValueRef.current;
    if (prevValue !== '' && value === '' && inputValue !== '') {
      onInputTextChange('');
    }
    prevValueRef.current = value;
  }, [value, onInputTextChange, inputValue]);

  // load data on mount to match the value from the url
  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  if (!data) return null;

  return (
    <StyledAutocomplete
      key={prevValueRef.current}
      freeSolo={false}
      filterOptions={(x) => x}
      value={value}
      data-cy={dataCy}
      open={open}
      options={options}
      onChange={handleChange}
      onOpen={handleOpen}
      onClose={handleClose}
      isOptionEqualToValue={(option, selectedValue) =>
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
        handleOptionSelected(option as any, selectedValue as any)
      }
      getOptionLabel={handleOptionLabel}
      disabled={disabled}
      loading={loading}
      renderInput={(params) => (
        <StyledTextField
          {...params}
          label={label}
          variant="outlined"
          size="small"
          data-cy={`${label}-input`}
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          slotProps={{
            input: {
              ...params.InputProps,
              startAdornment,
              endAdornment: (
                <>
                  {loading ? (
                    <CircularProgress color="inherit" size={20} />
                  ) : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  );
}
