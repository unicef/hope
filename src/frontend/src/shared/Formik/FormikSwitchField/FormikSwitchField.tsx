import { FormHelperText, Switch } from '@mui/material';
import { ReactElement } from 'react';
import styled from 'styled-components';

const StyledSwitch = styled.div`
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const StyledLabel = styled.span`
  font-weight: bold;
  font-size: 16px;
`;

export function FormikSwitchField({
  field,
  form,
  ...otherProps
}): ReactElement {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  return (
    <>
      <StyledSwitch>
        <StyledLabel>{otherProps.label}</StyledLabel>
        <Switch
          {...otherProps}
          checked={field.value}
          onChange={(e) => {
            form.handleChange({
              target: { name: field.name, value: e.target.checked },
            });
          }}
        />
      </StyledSwitch>
      {isInvalid && form.errors[field.name] && (
        <FormHelperText error>{form.errors[field.name]}</FormHelperText>
      )}
    </>
  );
}
