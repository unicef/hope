import { Box, Grid, Typography } from '@mui/material';
import Slider from '@mui/material/Slider';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

export const FormikSliderField = ({
  field,
  form,
  suffix,
  min,
  max,
  dataCy,
  ...otherProps
}): ReactElement => {
  const handleSliderChange = (_, newValue): void => {
    form.setFieldValue(field.name, newValue);
  };

  return (
    <Box sx={{ width: responsiveValue<number | string>('100%', 400) }}>
      <Typography variant="caption">{otherProps.label}</Typography>
      <Grid
        container
        spacing={2}
        sx={{
          alignItems: 'center',
        }}
      >
        <Slider
          {...otherProps}
          data-cy={dataCy}
          min={min}
          max={max}
          size="medium"
          value={typeof field.value === 'number' ? field.value : 0}
          onChange={handleSliderChange}
          aria-labelledby="input-slider"
        />
        <Grid size={2}>
          <p>
            {field.value}
            {suffix || null}
          </p>
        </Grid>
      </Grid>
    </Box>
  );
};
