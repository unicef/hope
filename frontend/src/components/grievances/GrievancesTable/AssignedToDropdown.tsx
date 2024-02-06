import React, { useEffect, useState } from 'react';
import Autocomplete from '@mui/lab/Autocomplete';
import styled from 'styled-components';
import { useDebounce } from '../../../hooks/useDebounce';
import TextField from '../../../shared/TextField';
import { useProgramContext } from '../../../programContext';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '180px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
  .MuiInput-underline:hover:not(.Mui-disabled):before,
  .MuiInput-underline:before,
  .MuiInput-underline:after {
    border: 0px;
  }
`;

export function AssignedToDropdown({
  fullWidth,
  onFilterChange,
  value,
  optionsData,
  setInputValue,
  ids,
  label,
  disableClearable,
}: {
  fullWidth?: boolean;
  onFilterChange?;
  value?;
  optionsData;
  setInputValue;
  ids?;
  label?;
  disableClearable?: boolean;
}): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { isActiveProgram } = useProgramContext();

  const onChangeMiddleware = (e, selectedValue): void => {
    e.preventDefault();
    e.stopPropagation();
    if (ids) {
      onFilterChange(selectedValue, ids);
    } else {
      onFilterChange(selectedValue);
    }
  };

  useEffect(() => {
    setInputValue(debouncedInputText);
  }, [debouncedInputText, setInputValue]);

  // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
  const sortOptionsDataByEmail = (options) => {
    options.sort((a, b) => {
      const emailA = a.node?.email?.toLowerCase();
      const emailB = b.node?.email?.toLowerCase();
      return emailA.localeCompare(emailB);
    });
    return options;
  };

  const sortedOptions = sortOptionsDataByEmail(optionsData);

  return (
    <StyledAutocomplete
      fullWidth={fullWidth}
      open={open}
      disableClearable={disableClearable}
      filterOptions={(options1) => options1}
      onChange={onChangeMiddleware}
      onOpen={(e) => {
        e.stopPropagation();
        setOpen(true);
      }}
      onClose={(e, reason) => {
        e.preventDefault();
        e.stopPropagation();
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => option.node.id === value1.id}
      getOptionLabel={(option) => {
        if (option.node) {
          return `${option.node.email}`;
        }
        return `${value?.email}`;
      }}
      value={value}
      options={sortedOptions}
      disabled={!isActiveProgram}
      renderInput={(params) => (
        <TextField
          {...params}
          margin="dense"
          value={inputValue}
          variant={label ? 'outlined' : 'standard'}
          label={label}
          onClick={(e) => {
            e.stopPropagation();
          }}
          onChange={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onInputTextChange(e.target.value);
          }}
          InputProps={{
            ...params.InputProps,
            endAdornment: <>{params.InputProps.endAdornment}</>,
          }}
        />
      )}
    />
  );
}
