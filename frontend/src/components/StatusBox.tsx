import { makeStyles } from '@material-ui/core/styles';
import { theme as themeObj } from '../theme';
import { opacityToHex } from '../utils/utils';
import React from 'react';

interface Props {
  status: string;
  statusToColor: (theme: typeof themeObj, status: string) => string;
}
const useStyles = makeStyles((theme: typeof themeObj) => ({
  statusBox: {
    color: ({ status, statusToColor }: Props) => statusToColor(theme, status),
    backgroundColor: ({ status, statusToColor }: Props) =>
      `${statusToColor(theme, status)}${opacityToHex(0.15)}`,
    borderRadius: '16px',
    fontFamily: 'Roboto',
    fontSize: '10px',
    fontWeight: 500,
    letterSpacing: '1.2px',
    lineHeight: '16px',
    padding: '3px',
    textAlign: 'center',
  },
}));

export function StatusBox({ status, statusToColor }: Props) {
  const classes = useStyles({ status, statusToColor });
  return <div className={classes.statusBox}>{status}</div>;
}
