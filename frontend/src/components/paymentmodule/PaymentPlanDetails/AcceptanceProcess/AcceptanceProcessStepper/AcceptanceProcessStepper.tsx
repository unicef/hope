import { Box } from '@material-ui/core';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import CancelIcon from '@material-ui/icons/Cancel';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ApprovalProcessNodeEdge } from '../../../../../__generated__/graphql';

const StyledBox = styled(Box)`
  width: 100%;
`;

const StyledCancelIcon = styled(CancelIcon)`
  color: #e90202;
`;

interface AcceptanceProcessStepperProps {
  row: ApprovalProcessNodeEdge;
  approvalNumberRequired: number;
  authorizationNumberRequired: number;
  financeReviewNumberRequired: number;
}

export const AcceptanceProcessStepper = ({
  row,
  approvalNumberRequired,
  authorizationNumberRequired,
  financeReviewNumberRequired,
}: AcceptanceProcessStepperProps): React.ReactElement => {
  const {
    sentForApprovalDate,
    sentForAuthorizationDate,
    sentForFinanceReviewDate,
    rejectedOn,
  } = row.node;
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
  const [activeStep, setActiveStep] = useState(() => getActiveStep());

  //TODO: Add numbers in steps
  //TODO: handle step completed prop based on numbers required

  const steps = [
    {
      name: `${t('Approval')} (0/${approvalNumberRequired})`,
      hasError: rejectedOn === 'IN_APPROVAL',
    },
    {
      name: `${t('Authorization')} (0/${authorizationNumberRequired})`,
      hasError: rejectedOn === 'IN_AUTHORIZATION',
    },
    {
      name: `${t('Finance Review')} (0/${financeReviewNumberRequired})`,
      hasError: rejectedOn === 'IN_REVIEW',
    },
  ];

  return (
    <StyledBox>
      <Stepper activeStep={activeStep}>
        {steps.map((step) => {
          return (
            <Step key={step.name}>
              <StepLabel
                error={step.hasError}
                StepIconComponent={step.hasError ? StyledCancelIcon : null}
              >
                {step.name}
              </StepLabel>
            </Step>
          );
        })}
      </Stepper>
    </StyledBox>
  );
};
