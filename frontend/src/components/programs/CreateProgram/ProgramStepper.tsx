import React from 'react';
import { Stepper, Step, StepButton } from '@mui/material';

interface StepData {
  title: string;
  description: string;
  dataCy: string;
}

interface ProgramStepperProps {
  step: number;
  setStep: (step: number) => void;
  stepsData: StepData[];
}

export const handleNext = async ({
  validateForm,
  stepFields,
  step,
  setStep,
  setFieldTouched,
}): Promise<void> => {
  const errors = await validateForm();
  const currentStepErrors = stepFields[step].some((field) => errors[field]);

  if (!currentStepErrors) {
    if (step < stepFields.length) {
      setStep(step + 1);
    }
  } else {
    stepFields[step].forEach((field) => setFieldTouched(field, true, false));
  }
};

export const ProgramStepper: React.FC<ProgramStepperProps> = ({
  step,
  setStep,
  stepsData,
}) => {
  return (
    <Stepper activeStep={step}>
      {stepsData.map((item, index) => (
        <Step key={item.title}>
          <StepButton data-cy={item.dataCy} onClick={() => setStep(index)}>
            {item.title}
          </StepButton>
        </Step>
      ))}
    </Stepper>
  );
};
