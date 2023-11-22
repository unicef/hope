import React from 'react';
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';

const FormLabelContainer = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing(3)}px;
  .MuiFormLabel-root {
    color: ${({ theme }) => theme.palette.text.primary};
  }
  .MuiFormLabel-root.Mui-focused {
    color: ${({ theme }) => theme.palette.text.primary};
  }
  .MuiFormLabel-root:focus {
    color: ${({ theme }) => theme.palette.text.primary};
  }
`;

export const FormikRadioGroup = ({
  field,
  form,
  ...otherProps
}): React.ReactElement => {
  return (
    <>
      <Box mt={otherProps.noMargin ? 0 : 6} mb={otherProps.noMargin ? 0 : 2}>
        <FormLabelContainer>
          <Typography variant='caption'>{otherProps.label}</Typography>
        </FormLabelContainer>
        <RadioGroup
          {...field}
          {...otherProps}
          name={field.name}
          value={form.values[field.name]}
          id={`radioGroup-${field.name}`}
        >
          {otherProps.choices.map((each) => (
            <Box p={1} mb={3} key={each.value}>
              <FormControlLabel
                key={each.value}
                value={each.value}
                label={each.name}
                control={<Radio color='primary' />}
              />
            </Box>
          ))}
        </RadioGroup>
      </Box>
    </>
  );
};
