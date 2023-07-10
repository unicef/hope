import { Button } from '@material-ui/core';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { CashPlanDetails } from '../../../components/core/CashPlanDetails/CashPlanDetails';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  CashPlanNode,
  useCashAssistUrlPrefixQuery,
  useCashPlanQuery,
} from '../../../__generated__/graphql';
import { PaymentRecordTable } from '../../tables/payments/PaymentRecordTable';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function CashPlanDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = useCashPlanQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: caData,
    loading: caPrefixLoading,
  } = useCashAssistUrlPrefixQuery({ fetchPolicy: 'cache-first' });
  const { baseUrl, isAllPrograms } = useBaseUrl();
  if (loading || caPrefixLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !caData || permissions === null) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: data.cashPlan.program.name,
      to: `/${baseUrl}/details/${data.cashPlan.program.id}/`,
    },
  ];

  if (isAllPrograms) {
    breadCrumbsItems.unshift({
      title: t('Programme Management'),
      to: `/${baseUrl}/list/`,
    });
  }

  const cashPlan = data.cashPlan as CashPlanNode;
  return (
    <div>
      <PageHeader
        title={`${t('Payment Plan')} #${data.cashPlan.caId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
      >
        <Button
          variant='contained'
          color='primary'
          component='a'
          disabled={!data.cashPlan.caHashId}
          target='_blank'
          href={`${caData.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_cashplan&id=${data.cashPlan.caHashId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          {t('Open in CashAssist')}
        </Button>
      </PageHeader>
      <Container>
        <CashPlanDetails cashPlan={cashPlan} baseUrl={baseUrl} />
        <TableWrapper>
          <PaymentRecordTable cashPlan={cashPlan} />
        </TableWrapper>
      </Container>
    </div>
  );
}
