import React from 'react';
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { GreyBox } from '../../../components/core/GreyBox';

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
  withGreyBox = false,
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
          {otherProps.choices.map(
            (each: {
              value: string;
              optionLabel?: string | React.ReactElement;
              name: string;
            }) => (
              <Box p={2} mb={2} key={each.value}>
                {withGreyBox ? (
                  <GreyBox p={2}>
                    <FormControlLabel
                      key={each.value}
                      value={each.value}
                      label={each.optionLabel || each.name}
                      control={<Radio color='primary' />}
                    />
                  </GreyBox>
                ) : (
                  <FormControlLabel
                    key={each.value}
                    value={each.value}
                    label={each.optionLabel || each.name}
                    control={<Radio color='primary' />}
                  />
                )}
              </Box>
            ),
          )}
        </RadioGroup>
      </Box>
    </>
  );
};
