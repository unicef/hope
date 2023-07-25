import { Step, StepLabel, Stepper } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

const NoRootPadding = styled.div`
  .MuiStepper-root {
    padding: 0 !important;
  }
`;

export interface CreateGrievanceStepperProps {
  activeStep: number;
  steps: string[];
}

export const CreateGrievanceStepper = ({
  activeStep,
  steps,
}: CreateGrievanceStepperProps): React.ReactElement => {
  return (
    <>
      <NoRootPadding>
        <Stepper activeStep={activeStep}>
          {steps.map((label) => {
            const stepProps: { completed?: boolean } = {};
            const labelProps: {
              optional?: React.ReactNode;
            } = {};
            return (
              <Step key={label} {...stepProps}>
                <StepLabel {...labelProps}>{label}</StepLabel>
              </Step>
            );
          })}
        </Stepper>
      </NoRootPadding>
    </>
  );
};
