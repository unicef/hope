import { ManagerialConsoleBaseModal } from './ManagerialConsoleBaseModal';
import { useTranslation } from 'react-i18next';

interface AuthorizePaymentPlansModalProps {
  selectedPlansIds: any[];
  selectedPlansUnicefIds: string[];
  onAuthorize: (plans: any[], comment: string) => Promise<void>;
}

export const AuthorizePaymentPlansModal = ({
  selectedPlansIds,
  selectedPlansUnicefIds,
  onAuthorize,
}: AuthorizePaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <ManagerialConsoleBaseModal
      selectedPlansIds={selectedPlansIds}
      selectedPlansUnicefIds={selectedPlansUnicefIds}
      buttonTitle={t('Authorize')}
      dialogTitle={t('Authorize Payment Plans')}
      title={t('Are you sure you want to authorize these Payment Plans?')}
      onSave={onAuthorize}
    />
  );
};
