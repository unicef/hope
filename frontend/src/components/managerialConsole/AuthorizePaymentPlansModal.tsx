import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface AuthorizePaymentPlansModalProps {
  selectedPlans: any[];
  onAuthorize: (plans: any[]) => Promise<void>;
}

export const AuthorizePaymentPlansModal = ({
  selectedPlans,
  onAuthorize,
}: AuthorizePaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <ManagerialConsoleBaseModal
      selectedPlans={selectedPlans}
      buttonTitle={t('Authorize')}
      dialogTitle={t('Authorize Payment Plans')}
      title={t('Are you sure you want to authorize these Payment Plans?')}
      onSave={onAuthorize}
    />
  );
};
