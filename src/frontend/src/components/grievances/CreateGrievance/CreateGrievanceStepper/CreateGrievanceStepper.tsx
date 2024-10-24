import { Step, StepLabel, Stepper } from '@mui/material';
import * as React from 'react';
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

export function CreateGrievanceStepper({
  activeStep,
  steps,
}: CreateGrievanceStepperProps): React.ReactElement {
  return (
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
  );
}
