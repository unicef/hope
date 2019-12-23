import React from 'react';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import { theme as themeObj } from '../theme';

const useStyles = makeStyles((theme: typeof themeObj) => ({
  label: {
    ...theme.hctTypography.label,
    textTransform: 'uppercase',
  },
  value: {
    color: '#253B46',
    ...theme.hctTypography.font,
    fontSize: '14px',
    lineHeight: '19px',
  },
}));

export interface Props {
  value?: React.ReactNode;
  children?: React.ReactElement;
  label: string;
}

export function LabelizedField({ value, children, label }: Props) {
  const classes = useStyles({ status: null });

  return (
    <div>
      <Typography className={classes.label} color='textSecondary'>
        {label}
      </Typography>
      <div>
        {children || (
          <Typography className={classes.value} color='textSecondary'>
            {value}
          </Typography>
        )}
      </div>
    </div>
  );
}
