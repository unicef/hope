import { Box, Radio, RadioGroup, Typography } from '@mui/material';
import styled from 'styled-components';
import { GreyBox } from '@components/core/GreyBox';
import { ReactElement } from 'react';

const FormLabelContainer = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing(3)};
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

export function FormikRadioGroup({
  field,
  form,
  withGreyBox = false,
  alignItems = 'start',
  ...otherProps
}): ReactElement {
  const handleChange = (event): void => {
    form.setFieldValue(field.name, event.target.value);
    if (otherProps.onChange) {
      otherProps.onChange(event);
    }
  };
  return (
    <Box mt={otherProps.noMargin ? 0 : 6} mb={otherProps.noMargin ? 0 : 2}>
      <FormLabelContainer>
        <Typography variant="caption">{otherProps.label}</Typography>
      </FormLabelContainer>
      <RadioGroup
        {...field}
        {...otherProps}
        onChange={handleChange}
        name={field.name}
        value={form.values[field.name]}
        id={`radioGroup-${field.name}`}
        key={form.values[field.name]}
      >
        {otherProps.choices.map(
          (each: {
            value: string;
            optionLabel?: string | ReactElement;
            name: string;
            dataCy?: string;
          }) => (
            <Box key={each.value}>
              <Box mb={1} display="flex" alignItems={alignItems}>
                <Radio
                  color="primary"
                  value={each.value}
                  checked={field.value === each.value}
                  data-cy={each?.dataCy}
                />
                {withGreyBox ? (
                  <GreyBox p={2}>
                    <Box ml={2}>{each.optionLabel || each.name}</Box>
                  </GreyBox>
                ) : (
                  <Box ml={2}>{each.optionLabel || each.name}</Box>
                )}
              </Box>
            </Box>
          ),
        )}
      </RadioGroup>
    </Box>
  );
}
