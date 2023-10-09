import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import CancelIcon from '@material-ui/icons/Cancel';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const StyledCancelIcon = styled(CancelIcon)`
  color: #e90202;
`;

interface AcceptanceProcessStepperProps {
  acceptanceProcess;
}

export const AcceptanceProcessStepper = ({
  acceptanceProcess,
}: AcceptanceProcessStepperProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    rejectedOn,
    actions,
    authorizationNumberRequired,
    releaseNumberRequired,
  } = acceptanceProcess;
  const steps = [
    {
      name: `${t('Authorization')} (${
        actions.authorization.length
      }/${authorizationNumberRequired})`,
      hasError: rejectedOn === 'IN_AUTHORIZATION',
      isCompleted: actions.authorization.length === authorizationNumberRequired,
    },
    {
      name: `${t('Release')} (${
        actions.release.length
      }/${releaseNumberRequired})`,
      hasError: rejectedOn === 'IN_REVIEW',
      isCompleted: actions.release.length === releaseNumberRequired,
    },
  ];
  const getActiveStep = (): number => {
    if (actions.release.length === releaseNumberRequired) {
      return 1;
    }
    return 0;
  };

  return (
    <Stepper activeStep={getActiveStep()}>
      {steps.map((step) => (
        <Step completed={step.isCompleted} key={step.name}>
          <StepLabel
            error={step.hasError}
            StepIconComponent={step.hasError ? StyledCancelIcon : null}
          >
            {step.name}
          </StepLabel>
        </Step>
      ))}
    </Stepper>
  );
};
