import React from 'react';
import {
  FormControl,
  FormControlLabel,
  FormLabel,
  RadioGroup,
  Radio,
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
const StyledFormControl = styled.div`
  margin-top: ${({ theme }) => theme.spacing(4)}px;
  margin-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

export const FormikRadioGroup = ({
  field,
  form,
  ...otherProps
}): React.ReactElement => {
  return (
    <>
      <StyledFormControl {...otherProps} component='fieldset'>
        <FormLabelContainer>
          <FormLabel component='legend'>{otherProps.label}</FormLabel>
        </FormLabelContainer>
        <RadioGroup
          {...field}
          {...otherProps}
          name={field.name}
          value={form.values[field.name]}
          id={`radioGroup-${field.name}`}
        >
          {otherProps.choices.map((each) => (
            <FormControlLabel
              key={each.value}
              value={each.value}
              label={each.name}
              control={<Radio color='primary' />}
            />
          ))}
        </RadioGroup>
      </StyledFormControl>
    </>
  );
};
