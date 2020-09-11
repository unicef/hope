import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import FlagIcon from '@material-ui/icons/Flag';
import { MiśTheme } from '../theme';

const useStyles = makeStyles((theme: MiśTheme) => ({
  warning: {
    color: theme.hctPalette.red,
  },
}));

export const Flag = (): React.ReactElement => {
  const classes = useStyles();
  return <FlagIcon className={classes.warning} />;
};
