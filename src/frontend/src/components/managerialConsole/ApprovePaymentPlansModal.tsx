import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface ApprovePaymentPlansModalProps {
  selectedPlansIds: any[];
  selectedPlansUnicefIds: string[];
  onApprove: (plans: any[], comment: string) => Promise<void>;
}

export const ApprovePaymentPlansModal = ({
  selectedPlansIds,
  selectedPlansUnicefIds,
  onApprove,
}: ApprovePaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <ManagerialConsoleBaseModal
      selectedPlansIds={selectedPlansIds}
      selectedPlansUnicefIds={selectedPlansUnicefIds}
      buttonTitle={t('Approve')}
      dialogTitle={t('Approve Payment Plans')}
      title={t('Are you sure you want to approve these Payment Plans?')}
      onSave={onApprove}
    />
  );
};
