import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { Title } from '../core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';

export const PaymentIds = ({
  verifications,
}: {
  verifications: GrievanceTicketQuery['grievanceTicket']['paymentVerificationTicketDetails']['paymentVerifications']['edges'];
}): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const mappedIds = verifications.map(
    (verification): React.ReactElement => (
      <Box mb={1}>
        <ContentLink
          href={`/${businessArea}/verification-records/${verification.node.id}`}
        >
          {verification.node.paymentRecord.caId}
        </ContentLink>
      </Box>
    ),
  );
  return (
    <ApproveBox>
      <Title>
        <Typography variant='h6'>{t('Payment Ids')}</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        {mappedIds}
      </Box>
    </ApproveBox>
  );
};
