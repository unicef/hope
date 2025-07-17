import { FC, useEffect, useState } from 'react';
import { TextField, Autocomplete } from '@mui/material';
import { useDebounce } from '@hooks/useDebounce';
import { useProgramContext } from '../../../programContext';
import { User } from '@restgenerated/models/User';
import styled from 'styled-components';

const StyledAutocomplete = styled(Autocomplete<User, false, boolean, false>)<{
  fullWidth?: boolean;
}>`
  width: ${(props) => (props.fullWidth ? '100%' : '180px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
  .MuiInput-underline:hover:not(.Mui-disabled):before,
  .MuiInput-underline:before,
  .MuiInput-underline:after {
    border: 0px;
  }
  .MuiFormControl-root {
    width: 260px;
  }
`;

interface AssignedToDropdownProps {
  fullWidth?: boolean;
  onFilterChange?: (selectedValue: User | null, ids?: any) => void;
  value?: User | null;
  optionsData: User[];
  setInputValue: (value: string) => void;
  ids?: any;
  label?: string;
  disableClearable?: boolean;
}

export const AssignedToDropdown: FC<AssignedToDropdownProps> = ({
  fullWidth,
  onFilterChange,
  value,
  optionsData,
  setInputValue,
  ids,
  label,
  disableClearable,
}) => {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputText] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { isActiveProgram } = useProgramContext();

  useEffect(() => {
    setInputValue(debouncedInputText);
  }, [debouncedInputText, setInputValue]);

  const sortedOptions = Array.isArray(optionsData)
    ? [...optionsData].sort((a, b) => {
        const emailA = a?.email?.toLowerCase();
        const emailB = b?.email?.toLowerCase();
        return emailA.localeCompare(emailB);
      })
    : [];

  const handleOpen = (e: any) => {
    e.stopPropagation();
    setOpen(true);
  };

  const handleClose = (e: any, reason: string) => {
    e.preventDefault();
    e.stopPropagation();
    setOpen(false);
    if (reason !== 'select-option') setInputText('');
  };

  const handleChange = (e: any, selectedValue: User | null) => {
    e.preventDefault();
    e.stopPropagation();
    if (ids) {
      onFilterChange?.(selectedValue, ids);
    } else {
      onFilterChange?.(selectedValue);
    }
  };

  const handleInputChange = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
    setInputText(e.target.value);
  };

  return (
    <StyledAutocomplete
      fullWidth={fullWidth}
      open={open}
      disableClearable={disableClearable}
      filterOptions={(options1) => options1}
      onChange={handleChange}
      onOpen={handleOpen}
      onClose={handleClose}
      isOptionEqualToValue={(option: User, value1: User) =>
        option.id === value1.id
      }
      getOptionLabel={(option: User) =>
        option ? `${option.email}` : `${value?.email || ''}`
      }
      value={value}
      options={sortedOptions}
      disabled={!isActiveProgram}
      renderInput={(params) => (
        <TextField
          {...params}
          value={inputValue}
          variant={label ? 'outlined' : 'standard'}
          label={label}
          onClick={(e) => e.stopPropagation()}
          onChange={handleInputChange}
          InputProps={{
            ...params.InputProps,
            endAdornment: <>{params.InputProps.endAdornment}</>,
          }}
        />
      )}
    />
  );
};
