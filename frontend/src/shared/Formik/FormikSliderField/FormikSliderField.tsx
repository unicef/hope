import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import { Typography } from '@material-ui/core';

const useStyles = makeStyles({
  root: {
    width: 400,
  },
});

export const FormikSliderField = ({
  field,
  form,
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles();

  const handleSliderChange = (event, newValue) => {
    form.setFieldValue(field.name, newValue);
  };

  return (
    <div className={classes.root}>
      <Typography variant='caption'>{otherProps.label}</Typography>
      <Grid container spacing={2} alignItems='center'>
        <Grid item xs>
          <Slider
            {...otherProps}
            value={typeof field.value === 'number' ? field.value : 0}
            onChange={handleSliderChange}
            aria-labelledby='input-slider'
          />
        </Grid>
        <Grid item>
          <p>{field.value}</p>
        </Grid>
      </Grid>
    </div>
  );
};
