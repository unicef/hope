import type { FC } from 'react';
import { Stepper, Step, StepButton } from '@mui/material';
import { useIsMobile } from 'src/responsive';

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
}: {
  validateForm: () => Promise<any>;
  stepFields: string[][];
  step: number;
  setStep: (step: number) => void;
  setFieldTouched: (
    field: string,
    touched: boolean,
    shouldValidate?: boolean,
  ) => void;
  values: any;
  setErrors: (errors: any) => void;
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

export const ProgramStepper: FC<ProgramStepperProps> = ({
  step,
  setStep,
  stepsData,
}) => {
  const isMobile = useIsMobile();
  // Side-by-side labels don't fit a phone; put them under the step icons there.
  return (
    <Stepper activeStep={step} alternativeLabel={isMobile}>
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
