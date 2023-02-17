import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import CancelIcon from '@material-ui/icons/Cancel';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

const StyledCancelIcon = styled(CancelIcon)`
  color: #e90202;
`;

interface AcceptanceProcessStepperProps {
  acceptanceProcess: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'][0]['node'];
}

export const AcceptanceProcessStepper = ({
  acceptanceProcess,
}: AcceptanceProcessStepperProps): React.ReactElement => {
  const { rejectedOn, actions, approvalNumberRequired, authorizationNumberRequired, financeReleaseNumberRequired } = acceptanceProcess;
  const { t } = useTranslation();
  const steps = [
    {
      name: `${t('Approval')} (${
        actions.approval.length
      }/${approvalNumberRequired})`,
      hasError: rejectedOn === 'IN_APPROVAL',
      isCompleted: actions.approval.length === approvalNumberRequired,
    },
    {
      name: `${t('Authorization')} (${
        actions.authorization.length
      }/${authorizationNumberRequired})`,
      hasError: rejectedOn === 'IN_AUTHORIZATION',
      isCompleted: actions.authorization.length === authorizationNumberRequired,
    },
    {
      name: `${t('Finance Release')} (${
        actions.financeRelease.length
      }/${financeReleaseNumberRequired})`,
      hasError: rejectedOn === 'IN_REVIEW',
      isCompleted:
        actions.financeRelease.length === financeReleaseNumberRequired,
    },
  ];
  const getActiveStep = (): number => {
    if (actions.authorization.length === authorizationNumberRequired) {
      return 2;
    }
    if (actions.approval.length === approvalNumberRequired) {
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
