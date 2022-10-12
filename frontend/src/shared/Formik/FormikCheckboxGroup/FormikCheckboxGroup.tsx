import { Box, Checkbox, FormControlLabel } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { FieldLabel } from '../../../components/core/FieldLabel';

export const FormikCheckboxGroup = ({
  field,
  ...otherProps
}): React.ReactElement => {
  return (
    <>
      <FieldLabel>{otherProps.label}</FieldLabel>
      <Box display='flex' flexDirection='column'>
        {otherProps.choices.map((each) => (
          <Field
            type='checkbox'
            name={field.name}
            value={each.value}
            key={each.name}
            as={FormControlLabel}
            control={
              <Checkbox
                color='primary'
                checked={otherProps.values[field.name]?.includes(each.value)}
              />
            }
            label={each.name}
          />
        ))}
      </Box>
    </>
  );
};
