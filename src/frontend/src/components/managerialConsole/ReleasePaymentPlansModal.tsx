import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface ReleasePaymentPlansModalProps {
  selectedPlansIds: string[];
  selectedPlansUnicefIds: string[];
  onRelease: (plans: any[], comment: string) => Promise<void>;
}

export const ReleasePaymentPlansModal = ({
  selectedPlansIds,
  selectedPlansUnicefIds,
  onRelease,
}: ReleasePaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <ManagerialConsoleBaseModal
      selectedPlansIds={selectedPlansIds}
      selectedPlansUnicefIds={selectedPlansUnicefIds}
      buttonTitle={t('Release')}
      dialogTitle={t('Release Payment Plans')}
      title={t('Are you sure you want to release these Payment Plans?')}
      onSave={onRelease}
    />
  );
};
