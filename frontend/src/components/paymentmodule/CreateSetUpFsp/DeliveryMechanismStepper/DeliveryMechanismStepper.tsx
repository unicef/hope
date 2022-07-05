import { Box } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import React, { useState } from 'react';

interface DeliveryMechanismStepperProps {
  activeStep: number;
  setActiveStep;
  children: React.ReactNode;
}

export const DeliveryMechanismStepper = ({
  children,
  activeStep,
  setActiveStep,
}: DeliveryMechanismStepperProps): React.ReactElement => {
  const steps = [
    'Choose Delivery Mechanism Order',
    'Assign FSP per Delivery Mechanism',
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <>
      <Stepper activeStep={activeStep}>
        {steps.map((label) => {
          return (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          );
        })}
      </Stepper>
      <div>{children}</div>
      <Box display='flex'>
        <Box mr={2}>
          <Button disabled={activeStep === 0} onClick={handleBack}>
            Back
          </Button>
        </Box>
        <Button variant='contained' color='primary' onClick={handleNext}>
          {activeStep === steps.length - 1 ? 'Save' : 'Next'}
        </Button>
      </Box>
    </>
  );
};
