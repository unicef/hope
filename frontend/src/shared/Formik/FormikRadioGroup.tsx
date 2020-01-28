import React from 'react';
import {
  FormControl,
  FormControlLabel,
  FormLabel,
  RadioGroup,
  Radio,
} from '@material-ui/core';

export const FormikRadioGroup = ({
  field,
  form,
  ...otherProps
}): React.ReactElement => {
  return (
    <>
      <FormControl {...otherProps} component='fieldset'>
        <FormLabel component='legend'>{otherProps.label}</FormLabel>
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
