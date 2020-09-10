import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Tooltip } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';
import { MiśTheme } from '../theme';

const useStyles = makeStyles((theme: MiśTheme) => ({
  warning: { color: theme.hctPalette.red },
}));

export const FlagTooltip = ({ message = '' }): React.ReactElement => {
  const classes = useStyles();
  return (
    <Tooltip title={message}>
      <WarningIcon className={classes.warning} />
    </Tooltip>
  );
};
