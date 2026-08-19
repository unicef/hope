import CircularProgress from '@mui/material/CircularProgress';
import {
  ReactElement,
  ReactNode,
  SyntheticEvent,
  useEffect,
  useRef,
} from 'react';
import { StyledAutocomplete, StyledTextField } from './StyledAutocomplete';
import { AutocompleteOption } from './types';

export function BaseAutocompleteFilterRest<TOption = AutocompleteOption>({
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
  loadData: () => void;
  loading: boolean;
  options: TOption[];
  handleChange: (event: SyntheticEvent, newValue: TOption | null) => void;

  handleClose: (event: SyntheticEvent, reason: string) => void;
  handleOptionSelected: (option: TOption | string, value: TOption | string) => boolean;
  handleOptionLabel: (option: TOption | string) => string;
  handleOpen: () => void;
  open: boolean;
  data: unknown;
  inputValue: string;
  onInputTextChange: (value: string) => void;
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
        handleOptionSelected(
          option as TOption | string,
          selectedValue as TOption | string,
        )
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
            ...params.slotProps,
            input: {
              ...params.slotProps.input,
              startAdornment,
              endAdornment: (
                <>
                  {loading ? (
                    <CircularProgress color="inherit" size={20} />
                  ) : null}
                  {params.slotProps.input.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  );
}
