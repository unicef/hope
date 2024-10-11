import * as React from 'react';
import { styled } from '@mui/system';
import Grid from '@mui/material/Grid';
import Slider from '@mui/material/Slider';
import { Typography, Box } from '@mui/material';

const StyledBox = styled(Box)({
  width: 400,
});

export const FormikSliderField = ({
  field,
  form,
  suffix,
  min,
  max,
  dataCy,
  ...otherProps
}): React.ReactElement => {
  const handleSliderChange = (_, newValue): void => {
    form.setFieldValue(field.name, newValue);
  };

  return (
    <StyledBox>
      <Typography variant="caption">{otherProps.label}</Typography>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs>
          <Slider
            {...otherProps}
            data-cy={dataCy}
            min={min}
            max={max}
            value={typeof field.value === 'number' ? field.value : 0}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
          />
        </Grid>
        <Grid item>
          <p>
            {field.value}
            {suffix || null}
          </p>
        </Grid>
      </Grid>
    </StyledBox>
  );
};
