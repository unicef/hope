import { Step, StepLabel, Stepper } from '@mui/material';
import type { ReactElement, ReactNode } from 'react';
import styled from 'styled-components';
import { useIsMobile } from 'src/responsive';

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
  const isMobile = useIsMobile();
  // Side-by-side labels don't fit a phone; put them under the step icons there.
  return (
    <NoRootPadding>
      <Stepper activeStep={activeStep} alternativeLabel={isMobile}>
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
