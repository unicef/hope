import { FC, useEffect, useState } from 'react';
import styled from 'styled-components';
import { TextField, Autocomplete } from '@mui/material';
import { useDebounce } from '@hooks/useDebounce';
import { useProgramContext } from '../../../programContext';
import { AllUsersForFiltersQuery } from '@generated/graphql';

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
  .MuiFormControl-root {
    width: 260px;
  }
`;

interface AssignedToDropdownProps {
  fullWidth?: boolean;
  onFilterChange?: (selectedValue: any, ids?: any) => void;
  value?: any;
  optionsData: any;
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

  const sortedOptions = [...optionsData].sort((a, b) => {
    const emailA = a.node?.email?.toLowerCase();
    const emailB = b.node?.email?.toLowerCase();
    return emailA.localeCompare(emailB);
  });

  const handleOpen = (e) => {
    e.stopPropagation();
    setOpen(true);
  };

  const handleClose = (e, reason: string) => {
    e.preventDefault();
    e.stopPropagation();
    setOpen(false);
    if (reason !== 'select-option') setInputText('');
  };

  const handleChange = (e, selectedValue) => {
    e.preventDefault();
    e.stopPropagation();
    if (ids) {
      onFilterChange(selectedValue, ids);
    } else {
      onFilterChange(selectedValue);
    }
  };

  const handleInputChange = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setInputText(e.target.value);
  };

  return (
    // @ts-ignore
    <StyledAutocomplete<AllUsersForFiltersQuery['allUsers']['edges']>
      fullWidth={fullWidth}
      open={open}
      disableClearable={disableClearable}
      filterOptions={(options1) => options1}
      onChange={handleChange}
      onOpen={handleOpen}
      onClose={handleClose}
      isOptionEqualToValue={(option, value1) => option.node.id === value1.id}
      getOptionLabel={(option) =>
        option.node ? `${option.node.email}` : `${value?.email}`
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
