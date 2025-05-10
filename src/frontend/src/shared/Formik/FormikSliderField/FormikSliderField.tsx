import { styled } from '@mui/system';
import Grid from '@mui/material/Grid2';
import Slider from '@mui/material/Slider';
import { Typography, Box } from '@mui/material';
import { ReactElement } from 'react';

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
}): ReactElement => {
  const handleSliderChange = (_, newValue): void => {
    form.setFieldValue(field.name, newValue);
  };

  return (
    <StyledBox>
      <Typography variant="caption">{otherProps.label}</Typography>
      <Grid container spacing={2} alignItems="center">
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
        <Grid>
          <p>
            {field.value}
            {suffix || null}
          </p>
        </Grid>
      </Grid>
    </StyledBox>
  );
};
