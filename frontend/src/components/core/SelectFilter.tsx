import { Box, IconButton, InputAdornment } from '@mui/material';
import { makeStyles } from '@mui/material/styles';
import { Close } from '@mui/icons-material';
import React from 'react';
import styled from 'styled-components';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import { StyledFormControl } from '../StyledFormControl';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;
const EndInputAdornment = styled(InputAdornment)`
  margin-right: 10px;
`;

const XIcon = styled(Close)`
  color: #707070;
`;

const useStyles = makeStyles(() => ({
  selectWrapper: {
    flex: 1,
    display: 'flex',
    maxWidth: '100%',
  },
  select: {
    flex: 1,
    maxWidth: '100%',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
}));

export const SelectFilter = ({
  label,
  children,
  onChange,
  icon = null,
  borderRadius = '4px',
  fullWidth = true,
  disableClearable = false,
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles();

  const checkValue = (value): boolean => {
    if (Array.isArray(value)) {
      return value.length > 0;
    }
    return Boolean(value);
  };

  const isValue = checkValue(otherProps.value);

  return (
    <div className={classes.selectWrapper}>
      <StyledFormControl
        theme={{ borderRadius }}
        fullWidth={fullWidth}
        variant="outlined"
        margin="dense"
      >
        <Box display="grid">
          <InputLabel>{label}</InputLabel>
          <Select
            /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
            // @ts-ignore
            className={classes.select}
            onChange={onChange}
            variant="outlined"
            label={label}
            MenuProps={{
              getContentAnchorEl: null,
            }}
            InputProps={{
              startAdornment: icon ? (
                <StartInputAdornment position="start">
                  {icon}
                </StartInputAdornment>
              ) : null,
              endAdornment:
                isValue && !disableClearable ? (
                  <EndInputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={() => {
                        onChange({
                          target: { value: otherProps.multiple ? [] : '' },
                        });
                      }}
                    >
                      <XIcon fontSize="small" />
                    </IconButton>
                  </EndInputAdornment>
                ) : null,
            }}
            {...otherProps}
          >
            {children}
          </Select>
        </Box>
      </StyledFormControl>
    </div>
  );
};
