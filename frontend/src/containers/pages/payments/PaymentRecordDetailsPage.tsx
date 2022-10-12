import { Box, Button } from '@material-ui/core';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { PaymentRecordDetails } from '../../../components/payments/PaymentRecordDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  PaymentRecordNode,
  PaymentRecordStatus,
  useCashAssistUrlPrefixQuery,
  usePaymentRecordQuery,
} from '../../../__generated__/graphql';
import { ForceFailedButton } from '../../../components/payments/ForceFailedButton';

export const PaymentRecordDetailsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  const { data, loading } = usePaymentRecordQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  if (loading || caLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
      permissions,
    )
  )
    return <PermissionDenied />;

  if (!data || !caData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme Management'),
      to: `/${businessArea}/programs/`,
    },
    {
      title: data.paymentRecord.parent.program.name,
      to: `/${businessArea}/programs/${data.paymentRecord.parent.program.id}/`,
    },
    {
      title: `Cash Plan #${data.paymentRecord.parent.caId}`,
      to: `/${businessArea}/cashplans/${data.paymentRecord.parent.id}`,
    },
  ];
  const paymentRecord = data.paymentRecord as PaymentRecordNode;
  return (
    <>
      <PageHeader
        title={`Payment ID ${paymentRecord.caId}`}
        breadCrumbs={breadCrumbsItems}
      >
        <>
          {hasPermissions(
            PERMISSIONS.PAYMENT_VERIFICATION_MARK_AS_FAILED,
            permissions,
          ) && (
            <ForceFailedButton
              paymentRecordId={paymentRecord.id}
              disabled={
                paymentRecord.status === PaymentRecordStatus.ForceFailed
              }
            />
          )}
          <Button
            variant='contained'
            color='primary'
            component='a'
            disabled={!paymentRecord.caHashId || !caData?.cashAssistUrlPrefix}
            target='_blank'
            href={`${caData?.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_payment&id=${paymentRecord.caHashId}`}
            startIcon={<OpenInNewRoundedIcon />}
          >
            {t('Open in CashAssist')}
          </Button>
        </>
      </PageHeader>
      <Box display='flex' flexDirection='column'>
        <PaymentRecordDetails
          paymentRecord={paymentRecord}
          canViewActivityLog={hasPermissions(
            PERMISSIONS.ACTIVITY_LOG_VIEW,
            permissions,
          )}
        />
      </Box>
    </>
  );
};
