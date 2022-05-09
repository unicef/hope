import { Box, Button } from '@material-ui/core';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import {
  decodeIdString,
  targetPopulationStatusMapping,
  targetPopulationStatusToColor,
} from '../../../../utils/utils';
import { StatusBox } from '../../../core/StatusBox';
import { TargetPopulationStatus } from '../../../../__generated__/graphql';
import { OpenPaymenPlanHeaderButtons } from './OpenPaymenPlanHeaderButtons';

const StatusWrapper = styled.div`
  width: 140px;
  margin-left: 30px;
`;

interface PaymentPlanDetailsHeaderProps {
  businessArea: string;
  permissions: string[];
  paymentPlan;
}

export function PaymentPlanDetailsHeader({
  businessArea,
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/`,
    },
  ];

  //TODO: Use statuses from node - not in backend yet
  let buttons;
  switch (paymentPlan?.status) {
    case 'OPEN':
      buttons = (
        <>
          {/* <OpenPaymenPlanHeaderButtons
          targetPopulation={targetPopulation}
          setEditState={setEditState}
          canDuplicate={canDuplicate}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        /> */}
        </>
      );
      break;
    default:
      buttons = <div>buttons</div>;
      break;
  }

  return (
    <PageHeader
      title={
        <Box display='flex' alignItems='center'>
          {t('Payment Plan')} ID ${decodeIdString(id)}
          <StatusWrapper>
            <StatusBox
              status={paymentPlan?.status}
              statusToColor={targetPopulationStatusToColor}
              statusNameMapping={targetPopulationStatusMapping}
            />
          </StatusWrapper>
        </Box>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      {buttons}
    </PageHeader>
  );
}
