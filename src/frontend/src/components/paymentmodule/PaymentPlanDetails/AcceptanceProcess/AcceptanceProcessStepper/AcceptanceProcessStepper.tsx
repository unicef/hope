import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Stepper from '@mui/material/Stepper';
import { useTranslation } from 'react-i18next';
import type { ReactElement } from 'react';
import type { ApprovalProcess } from '@restgenerated/models/ApprovalProcess';

interface AcceptanceProcessStepperProps {
  acceptanceProcess: ApprovalProcess;
  isClosed: boolean;
}

export function AcceptanceProcessStepper({
  acceptanceProcess,
  isClosed,
}: AcceptanceProcessStepperProps): ReactElement {
  const {
    rejectedOn,
    actions,
    approvalNumberRequired,
    authorizationNumberRequired,
    financeReleaseNumberRequired,
  } = acceptanceProcess;
  const { t } = useTranslation();
  const steps = [
    {
      name: `${t('Approval')} (${
        actions?.approval?.length
      }/${approvalNumberRequired})`,
      hasError: rejectedOn === 'IN_APPROVAL',
      isCompleted: actions?.approval?.length === approvalNumberRequired,
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
    {
      name: `${t('Finance Closure')} (${isClosed ? 1 : 0}/1)`,
      hasError: false,
      isCompleted: isClosed,
    },
  ];
  const getActiveStep = (): number => {
    if (isClosed) {
      return 3;
    }
    if (actions.authorization.length === authorizationNumberRequired) {
      return 2;
    }
    if (actions.approval?.length === approvalNumberRequired) {
      return 1;
    }
    return 0;
  };

  return (
    <Stepper activeStep={getActiveStep()}>
      {steps.map((step) => (
        <Step completed={step.isCompleted} key={step.name}>
          <StepLabel error={step.hasError}>{step.name}</StepLabel>
        </Step>
      ))}
    </Stepper>
  );
}
