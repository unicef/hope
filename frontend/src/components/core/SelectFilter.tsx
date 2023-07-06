import { Box, InputAdornment } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import React from 'react';
import styled from 'styled-components';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import { StyledFormControl } from '../StyledFormControl';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
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
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles();

  return (
    <div className={classes.selectWrapper}>
      <StyledFormControl
        borderRadius={borderRadius}
        fullWidth={fullWidth}
        variant='outlined'
        margin='dense'
      >
        <Box display='grid'>
          <InputLabel>{label}</InputLabel>
          <Select
            /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
            // @ts-ignore
            className={classes.select}
            onChange={onChange}
            variant='outlined'
            label={label}
            MenuProps={{
              getContentAnchorEl: null,
            }}
            InputProps={
              icon
                ? {
                    startAdornment: (
                      <StartInputAdornment position='start'>
                        {icon}
                      </StartInputAdornment>
                    ),
                  }
                : null
            }
            {...otherProps}
          >
            {children}
          </Select>
        </Box>
      </StyledFormControl>
    </div>
  );
};
