import { Box } from '@material-ui/core';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const StyledBox = styled(Box)`
  width: 100%;
`;

export const AcceptanceProcessStepper = (): React.ReactElement => {
  const { t } = useTranslation();
  const [activeStep, setActiveStep] = useState(1);
  const steps = [t('Approval'), t('Authorization'), t('Finance Review')];

  return (
    <StyledBox>
      <Stepper activeStep={activeStep}>
        {steps.map((label) => {
          return (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          );
        })}
      </Stepper>
    </StyledBox>
  );
};
