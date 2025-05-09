import { Box, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { LoadingButton } from '@components/core/LoadingButton';

const StatusWrapper = styled.div`
  margin-left: 30px;
`;

interface EditPaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  baseUrl: string;
  permissions: string[];
  paymentPlan: PaymentPlanDetail;
  loadingUpdate: boolean;
}

export function EditPaymentPlanHeader({
  handleSubmit,
  baseUrl,
  permissions,
  paymentPlan,
  loadingUpdate,
}: EditPaymentPlanHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { id, isFollowUp } = paymentPlan;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${id}`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="center">
          {t(isFollowUp ? 'Follow-up Payment Plan' : 'Payment Plan')} ID{' '}
          {paymentPlan.unicefId}
          <StatusWrapper>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </StatusWrapper>
          {paymentPlan.backgroundActionStatus && (
            <StatusWrapper>
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            </StatusWrapper>
          )}
        </Box>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display="flex" mt={2} mb={2}>
        <Box mr={3}>
          <Button
            component={Link}
            to={`/${baseUrl}/payment-module/payment-plans/${id}`}
          >
            {t('Cancel')}
          </Button>
        </Box>
        <LoadingButton
          loading={loadingUpdate}
          variant="contained"
          color="primary"
          onClick={handleSubmit}
        >
          {t('Save')}
        </LoadingButton>
      </Box>
    </PageHeader>
  );
}
