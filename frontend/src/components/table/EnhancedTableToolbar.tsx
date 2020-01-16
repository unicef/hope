import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import React from 'react';
import { createStyles, lighten, makeStyles, Theme, } from '@material-ui/core/styles';

interface EnhancedTableToolbarProps {
  title: string;
}

const useToolbarStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      paddingLeft: theme.spacing(2),
      paddingRight: theme.spacing(1),
    },
    highlight:
      theme.palette.type === 'light'
        ? {
            color: theme.palette.secondary.main,
            backgroundColor: lighten(theme.palette.secondary.light, 0.85),
          }
        : {
            color: theme.palette.text.primary,
            backgroundColor: theme.palette.secondary.dark,
          },
    title: {
      flex: '1 1 100%',
    },
  }),
);

export function EnhancedTableToolbar({
  title,
}: EnhancedTableToolbarProps): React.ReactElement {
  const classes = useToolbarStyles({});

  return (
    <Toolbar className={classes.root}>
      <Typography className={classes.title} variant='h6'>
        {title}
      </Typography>
    </Toolbar>
  );
}
