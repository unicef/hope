import { LockedPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons';
import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import type { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';

interface PaymentPlanDetailsHeaderProps {
  permissions: string[];
  paymentPlan: PaymentPlanDetail;
}

export const PaymentPlanDetailsHeader = ({
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const programCycleId = paymentPlan.programCycle?.id;
  const { data: programCycleData } = useQuery<ProgramCycleList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsCyclesRetrieve,
      {
        businessAreaSlug: businessArea,
        id: programCycleId,
        programCode: programId,
      },
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsCyclesRetrieve({
        businessAreaSlug: businessArea,
        id: programCycleId,
        programCode: programId,
      });
    },
    enabled: !!programCycleId,
  });

  const breadCrumbsItems: BreadCrumbsItem[] = [];

  if (programCycleId) {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '../../..',
    });
    breadCrumbsItems.push({
      title: `${programCycleData?.title || ''}`,
      to: '../..',
    });
  } else {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '..',
    });
  }

  const canRemove =
    hasPermissions(PERMISSIONS.PM_CREATE, permissions) && paymentPlan.canDelete;
  const canEdit = hasPermissions(PERMISSIONS.PM_CREATE, permissions);
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);

  let buttons: ReactElement | null = null;
  switch (paymentPlan.status) {
    case PaymentPlanStatusEnum.OPEN:
      buttons = (
        <OpenPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case PaymentPlanStatusEnum.LOCKED:
      buttons = (
        <LockedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canLock}
        />
      );
      break;
    case PaymentPlanStatusEnum.CLOSED:
      buttons = null;
      break;
    default:
      break;
  }

  return (
    <PageHeader
      title={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          {t('Payment Plan')} ID:{' '}
          <Box
            sx={{
              ml: 1,
              mr: 2,
            }}
          >
            <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
          </Box>
          <Box
            sx={{
              mr: 2,
            }}
          >
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </Box>
          <Box
            sx={{
              mr: 2,
            }}
          >
            {paymentPlan.backgroundActionStatus && (
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            )}
          </Box>
        </Box>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
      flags={<AdminButton adminUrl={paymentPlan.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
};
