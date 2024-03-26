import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface ReleasePaymentPlansModalProps {
  selectedPlans: any[];
  onRelease: (plans: any[]) => Promise<void>;
}

export const ReleasePaymentPlansModal = ({
  selectedPlans,
  onRelease,
}: ReleasePaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <ManagerialConsoleBaseModal
      selectedPlans={selectedPlans}
      buttonTitle={t('Release')}
      dialogTitle={t('Release Payment Plans')}
      title={t('Are you sure you want to release these Payment Plans?')}
      onSave={onRelease}
    />
  );
};
