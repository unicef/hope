import CircularProgress from '@material-ui/core/CircularProgress';
import React, { useEffect, useRef } from 'react';
import TextField from '../TextField';
import { StyledAutocomplete } from './StyledAutocomplete';

export const BaseAutocomplete = ({
  value,
  disabled,
  label,
  dataCy,
  loadData,
  loading,
  allEdges,
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
}: {
  value: string;
  disabled?: boolean;
  label: string;
  dataCy?: string;
  loadData;
  loading: boolean;
  allEdges;
  handleChange: (event, newValue) => void;
  //eslint-disable-next-line @typescript-eslint/no-explicit-any
  handleClose: (_: any, reason: string) => void;
  handleOptionSelected: (option, value) => boolean;
  handleOptionLabel: (option) => string;
  handleOpen: () => void;
  open: boolean;
  data;
  inputValue: string;
  onInputTextChange: (value) => void;
  debouncedInputText: string;
}): React.ReactElement => {
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
      value={value}
      data-cy={dataCy}
      open={open}
      filterOptions={(options1) => options1}
      onChange={handleChange}
      onOpen={handleOpen}
      onClose={handleClose}
      getOptionSelected={handleOptionSelected}
      getOptionLabel={handleOptionLabel}
      disabled={disabled}
      options={allEdges}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
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
