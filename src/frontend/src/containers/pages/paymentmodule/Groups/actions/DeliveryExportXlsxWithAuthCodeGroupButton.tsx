import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';
import { GroupExportXlsxDialog } from './GroupExportXlsxDialog';

interface DeliveryExportXlsxWithAuthCodeGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxWithAuthCodeGroupButton({
  group,
}: DeliveryExportXlsxWithAuthCodeGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  return (
    <GroupExportXlsxDialog
      groupId={group?.id ?? ''}
      buttonLabel={t('Export with Auth Code')}
      dialogTitle={t('Export with Auth Code')}
      buttonVariant="outlined"
      disabled={!group || isGroupBackgroundActionBusy(group)}
      dataCySuffix="delivery-export-xlsx-with-auth-code-group"
    />
  );
}
