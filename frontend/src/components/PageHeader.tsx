import { makeStyles } from '@material-ui/core/styles';
import { theme as themeObj } from '../theme';
import React from 'react';
import { Typography } from '@material-ui/core';

const useStyles = makeStyles((theme: typeof themeObj) => ({
  container: {
    backgroundColor: '#fff',
    padding: '26px 44px',
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '20px',
    boxShadow:
      '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
  },
}));

interface Props {
  title: string;
  children?: React.ReactElement;
}

export function PageHeader({ title, children }: Props) {
  const classes = useStyles({});
  return (
    <div className={classes.container}>
      <Typography variant='h5'>{title}</Typography>
      {children || null}
    </div>
  );
}
