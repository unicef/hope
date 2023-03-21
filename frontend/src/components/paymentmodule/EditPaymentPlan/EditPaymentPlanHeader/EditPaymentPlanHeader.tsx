import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '../../../../utils/utils';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { StatusBox } from '../../../core/StatusBox';

const StatusWrapper = styled.div`
  width: 140px;
  margin-left: 30px;
`;

interface EditPaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  businessArea: string;
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const EditPaymentPlanHeader = ({
  handleSubmit,
  businessArea,
  permissions,
  paymentPlan,
}: EditPaymentPlanHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = paymentPlan;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/payment-plans/${id}`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box display='flex' alignItems='center'>
          {t('Payment Plan')} ID {paymentPlan.unicefId}
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
      <Box display='flex' mt={2} mb={2}>
        <Box mr={3}>
          <Button
            component={Link}
            to={`/${businessArea}/payment-module/payment-plans/${id}`}
          >
            {t('Cancel')}
          </Button>
        </Box>
        <Button variant='contained' color='primary' onClick={handleSubmit}>
          {t('Save')}
        </Button>
      </Box>
    </PageHeader>
  );
};
