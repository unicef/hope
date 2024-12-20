import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { PaymentRecordAndPaymentNode, PaymentVerificationNode } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ContentLink } from '@core/ContentLink';
import { Title } from '@core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { ReactElement } from 'react';

type VerificationId = {
  id: PaymentVerificationNode['id'];
  caId: PaymentRecordAndPaymentNode['caId'];
};

interface PaymentIdsProps {
  verifications: VerificationId[];
}

export function PaymentIds({ verifications }: PaymentIdsProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const mappedIds = verifications.map(
    (verification): ReactElement => (
      <Box key={verification.id} mb={1}>
        <ContentLink
          href={`/${baseUrl}/verification-records/${verification.id}`}
        >
          {verification.caId}
        </ContentLink>
      </Box>
    ),
  );
  return (
    <ApproveBox>
      <Title>
        <Typography variant="h6">{t('Payment Ids')}</Typography>
      </Title>
      <Box display="flex" flexDirection="column">
        {mappedIds}
      </Box>
    </ApproveBox>
  );
}
