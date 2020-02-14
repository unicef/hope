import React from 'react';
import {
  FormControl,
  FormControlLabel,
  FormLabel,
  RadioGroup,
  Radio,
} from '@material-ui/core';
import styled from 'styled-components';

const StyledFormLabel = styled(FormLabel)`
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

const FormLabelContainer = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

export const FormikRadioGroup = ({
  field,
  form,
  ...otherProps
}): React.ReactElement => {
  return (
    <>
      <FormControl {...otherProps} component='fieldset'>
        <StyledFormLabel>
          <FormLabel component='legend'>{otherProps.label}</FormLabel>
        </StyledFormLabel>
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
      </FormControl>
    </>
  );
};
