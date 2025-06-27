import {
  Box,
  IconButton,
  InputAdornment,
  InputLabel,
  Select,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import styled from 'styled-components';
import { StyledFormControl } from '../StyledFormControl';
import { ReactElement, Children, isValidElement } from 'react';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;
const EndInputAdornment = styled(InputAdornment)`
  margin-right: 10px;
`;

const XIcon = styled(Close)`
  color: #707070;
`;

const SelectWrapper = styled.div`
  flex: 1;
  display: flex;
  max-width: 100%;
`;

const StyledSelect = styled(Select)`
  && .MuiOutlinedInput-input {
    padding-right: 10px !important;
  }
  flex: 1;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const OverflowDiv = styled.div`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
`;

export const SelectFilter = ({
  label,
  children,
  onChange,
  icon = null,
  fullWidth = true,
  disableClearable = false,
  dataCy = 'select-filter',
  ...otherProps
}): ReactElement => {
  const checkValue = (value): boolean => {
    if (Array.isArray(value)) {
      return value.length > 0;
    }
    return Boolean(value);
  };

  const isValue = checkValue(otherProps.value);

  return (
    <SelectWrapper>
      <StyledFormControl
        fullWidth={fullWidth}
        variant="outlined"
        size="small"
        data-cy={dataCy}
      >
        <Box display="flex" alignItems="center">
          <InputLabel>{label}</InputLabel>
          <StyledSelect
            size="small"
            onChange={onChange}
            variant="outlined"
            label={label}
            MenuProps={{
              anchorOrigin: {
                vertical: 'bottom',
                horizontal: 'left',
              },
              transformOrigin: {
                vertical: 'top',
                horizontal: 'left',
              },
            }}
            renderValue={(selected) => {
              const selectedValues = Array.isArray(selected)
                ? selected
                : [selected];

              const selectedOptions = Children.toArray(children).filter(
                (child): child is ReactElement<any> =>
                  isValidElement(child) &&
                  selectedValues.includes((child as ReactElement<any>).props.value),
              );

              return (
                <Box display="flex" alignItems="center">
                  {icon && (
                    <StartInputAdornment position="start">
                      {icon}
                    </StartInputAdornment>
                  )}
                  <OverflowDiv>
                    {selectedOptions
                      .map((option) => option.props.children)
                      .join(' ')}
                  </OverflowDiv>
                </Box>
              );
            }}
            endAdornment={
              isValue &&
              !disableClearable && (
                <EndInputAdornment position="end">
                  <IconButton
                    size="medium"
                    onMouseDown={(event) => {
                      event.preventDefault();
                      onChange({
                        target: { value: otherProps.multiple ? [] : '' },
                      });
                    }}
                  >
                    <XIcon fontSize="small" />
                  </IconButton>
                </EndInputAdornment>
              )
            }
            {...otherProps}
          >
            {children}
          </StyledSelect>
        </Box>
      </StyledFormControl>
    </SelectWrapper>
  );
};
