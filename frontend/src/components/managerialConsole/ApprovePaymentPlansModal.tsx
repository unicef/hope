import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface ApprovePaymentPlansModalProps {
  selectedPlans: any[];
  onApprove: (plans: any[], comment: string) => Promise<void>;
}

export const ApprovePaymentPlansModal = ({
  selectedPlans,
  onApprove,
}: ApprovePaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <ManagerialConsoleBaseModal
      selectedPlans={selectedPlans}
      buttonTitle={t('Approve')}
      dialogTitle={t('Approve Payment Plans')}
      title={t('Are you sure you want to approve these Payment Plans?')}
      onSave={onApprove}
    />
  );
};
