import React from 'react';
import { FormHelperText, Switch } from '@material-ui/core';
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

export const FormikSwitchField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}) => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  return (
    <>
      <StyledSwitch>
        <StyledLabel>{otherProps.label}</StyledLabel>
        <Switch {...otherProps} />
      </StyledSwitch>
      {isInvalid && form.errors[field.name] && (
        <FormHelperText error>{form.errors[field.name]}</FormHelperText>
      )}
    </>
  );
};
