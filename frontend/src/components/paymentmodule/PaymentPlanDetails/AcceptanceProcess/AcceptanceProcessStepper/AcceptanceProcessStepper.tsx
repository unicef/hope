import { Box } from '@material-ui/core';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import CancelIcon from '@material-ui/icons/Cancel';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

const StyledBox = styled(Box)`
  width: 100%;
`;

const StyledCancelIcon = styled(CancelIcon)`
  color: #e90202;
`;

interface AcceptanceProcessStepperProps {
  acceptanceProcess: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'][0]['node'];
  approvalNumberRequired: number;
  authorizationNumberRequired: number;
  financeReviewNumberRequired: number;
}

export const AcceptanceProcessStepper = ({
  acceptanceProcess,
  approvalNumberRequired,
  authorizationNumberRequired,
  financeReviewNumberRequired,
}: AcceptanceProcessStepperProps): React.ReactElement => {
  const {
    sentForApprovalDate,
    sentForAuthorizationDate,
    sentForFinanceReviewDate,
    rejectedOn,
    actions,
  } = acceptanceProcess;

  const { t } = useTranslation();
  const getActiveStep = (): number => {
    if (sentForFinanceReviewDate) {
      return 2;
    }
    if (sentForAuthorizationDate) {
      return 1;
    }

    if (sentForApprovalDate) {
      return 0;
    }
    return 0;
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [activeStep, setActiveStep] = useState(() => getActiveStep());

  const steps = [
    {
      name: `${t('Approval')} (${actions.approval.length}/${approvalNumberRequired})`,
      hasError: rejectedOn === 'IN_APPROVAL',
      isCompleted: actions.approval.length === approvalNumberRequired,
    },
    {
      name: `${t('Authorization')} (${actions.authorization.length}/${authorizationNumberRequired})`,
      hasError: rejectedOn === 'IN_AUTHORIZATION',
      isCompleted: actions.authorization.length === authorizationNumberRequired,
    },
    {
      name: `${t('Finance Review')} (${actions.financeReview.length}/${financeReviewNumberRequired})`,
      hasError: rejectedOn === 'IN_REVIEW',
      isCompleted: actions.financeReview.length === financeReviewNumberRequired,
    },
  ];

  return (
    <StyledBox>
      <Stepper activeStep={activeStep}>
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
    </StyledBox>
  );
};
