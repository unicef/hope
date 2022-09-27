import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { Box } from '@material-ui/core';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '../../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../../utils/utils';
import { useAccountabilityCommunicationMessageQuery } from '../../../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { CommunicationDetails } from '../../../../components/accountability/Communication/CommunicationDetails';
import { CommunicationMessageDetails } from '../../../../components/accountability/Communication/CommunicationMessageDetails';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { RecipientsTable } from '../../../tables/Communication/RecipientsTable';

export function CommunicationDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading, error } = useAccountabilityCommunicationMessageQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const permissions = usePermissions();

  if (loading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const message = data.accountabilityCommunicationMessage;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Communication'),
      to: `/${businessArea}/accountability/communication`,
    },
  ];
  return (
    <div>
      <PageHeader
        title={`${message.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
      />
      <Box display='flex' flexDirection='column'>
        <CommunicationDetails message={message} />
        <CommunicationMessageDetails message={message} />
        <RecipientsTable
          canViewDetails={hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            permissions,
          )}
          id={id}
        />
        {hasPermissions(
          PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
          permissions,
        ) && <UniversalActivityLogTable objectId={id} />}
      </Box>
    </div>
  );
}
