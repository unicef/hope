import { ReactElement } from 'react';
import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface ApprovePaymentPlansModalProps {
  selectedPlansIds: string[];
  selectedPlansUnicefIds: string[];
  onApprove: (plans: string[], comment: string) => Promise<void>;
}

export const ApprovePaymentPlansModal = ({
  selectedPlansIds,
  selectedPlansUnicefIds,
  onApprove,
}: ApprovePaymentPlansModalProps): ReactElement => {
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
