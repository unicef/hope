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
  values,
  setErrors,
}): Promise<void> => {
  const errors = await validateForm();
  const currentStepErrors = stepFields[step].some((field) => errors[field]);

  const initialPduFieldState = {
    name: '',
    pduData: {
      subtype: '',
      numberOfRounds: null,
      roundsNames: [],
    },
  };

  const isAllPduFieldsValidOrInitial = values.pduFields.every((pduField) => {
    const isInitialState =
      pduField.name === initialPduFieldState.name &&
      pduField.pduData.subtype === initialPduFieldState.pduData.subtype &&
      pduField.pduData.numberOfRounds ===
        initialPduFieldState.pduData.numberOfRounds &&
      pduField.pduData.roundsNames.length ===
        initialPduFieldState.pduData.roundsNames.length;

    const isValidState =
      pduField.name &&
      pduField.pduData.subtype &&
      pduField.pduData.numberOfRounds &&
      pduField.pduData.roundsNames.length === pduField.pduData.numberOfRounds;

    return isInitialState || isValidState;
  });

  if (!isAllPduFieldsValidOrInitial) {
    setErrors({
      ...errors,
      pduFields: 'Please complete the PDU fields correctly.',
    });
    stepFields[step].forEach((field) => setFieldTouched(field, true, false));
    return;
  }

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
