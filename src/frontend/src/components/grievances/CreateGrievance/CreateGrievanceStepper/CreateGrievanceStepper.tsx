import { Step, StepLabel, Stepper } from '@mui/material';
import { ReactElement, ReactNode } from 'react';
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
}: CreateGrievanceStepperProps): ReactElement {
  return (
    <NoRootPadding>
      <Stepper activeStep={activeStep}>
        {steps.map((label) => {
          const stepProps: { completed?: boolean } = {};
          const labelProps: {
            optional?: ReactNode;
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
