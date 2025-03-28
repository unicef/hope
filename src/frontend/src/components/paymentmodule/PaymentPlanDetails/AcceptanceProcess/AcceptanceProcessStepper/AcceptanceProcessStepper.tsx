import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Stepper from '@mui/material/Stepper';
import { useTranslation } from 'react-i18next';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface AcceptanceProcessStepperProps {
  acceptanceProcess: PaymentPlanDetail['approval_process'][0];
}

export function AcceptanceProcessStepper({
  acceptanceProcess,
}: AcceptanceProcessStepperProps): ReactElement {
  const {
    rejected_on,
    actions,
    approval_number_required,
    authorization_number_required,
    finance_release_number_required,
  } = acceptanceProcess;
  const { t } = useTranslation();
  const steps = [
    {
      name: `${t('Approval')} (${
        actions?.approval?.length
      }/${approval_number_required})`,
      hasError: rejected_on === 'IN_APPROVAL',
      isCompleted: actions?.approval?.length === approval_number_required,
    },
    {
      name: `${t('Authorization')} (${
        actions.authorization.length
      }/${authorization_number_required})`,
      hasError: rejected_on === 'IN_AUTHORIZATION',
      isCompleted:
        actions.authorization.length === authorization_number_required,
    },
    {
      name: `${t('Finance Release')} (${
        actions.financeRelease.length
      }/${finance_release_number_required})`,
      hasError: rejected_on === 'IN_REVIEW',
      isCompleted:
        actions.financeRelease.length === finance_release_number_required,
    },
  ];
  const getActiveStep = (): number => {
    if (actions.authorization.length === authorization_number_required) {
      return 2;
    }
    if (actions.approval?.length === approval_number_required) {
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
