import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import { PageHeader } from '../../components/PageHeader';
import { CashPlanDetails } from '../../components/CashPlanDetails';
import { PaymentRecordTable } from '../tables/PaymentRecordTable';
import {
  useCashPlanQuery,
  CashPlanNode,
  useCashAssistUrlPrefixQuery,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';
import { isPermissionDeniedError } from '../../utils/utils';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
`;

export function CashPlanDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = useCashPlanQuery({
    variables: { id },
  });
  const { data: caData, loading: caPrefixLoading, } = useCashAssistUrlPrefixQuery();
  const businessArea = useBusinessArea();

  if (loading || caPrefixLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !caData || permissions === null) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Management',
      to: `/${businessArea}/programs/`,
    },
    {
      title: data.cashPlan.program.name,
      to: `/${businessArea}/programs/${data.cashPlan.program.id}/`,
    },
  ];
  const cashPlan = data.cashPlan as CashPlanNode;
  return (
    <div>
      <PageHeader
        title={`Cash Plan #${data.cashPlan.caId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS,
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
          target="_blank"
          href={`${caData.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_cashplan&id=${data.cashPlan.caHashId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          Open in CashAssist
        </Button>
      </PageHeader>
      <Container>
        <CashPlanDetails cashPlan={cashPlan} />
        <TableWrapper>
          <PaymentRecordTable cashPlan={cashPlan} businessArea={businessArea} />
        </TableWrapper>
      </Container>
    </div>
  );
}
