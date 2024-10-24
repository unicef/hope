import * as React from 'react';
import { useState } from 'react';
import Button from '@mui/material/Button';
import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '@generated/graphql';
import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';

interface RelatedFollowUpPaymentPlansProps {
  baseUrl: string;
  followUps: PaymentPlanQuery['paymentPlan']['followUps'];
}

export function RelatedFollowUpPaymentPlans({
  followUps,
  baseUrl,
}: RelatedFollowUpPaymentPlansProps): React.ReactElement {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);

  const handleButtonClick = (): void => {
    setShowAll(!showAll);
  };

  let followUpLinks = null;
  if (followUps?.edges?.length > 0) {
    const truncatedFollowUps = showAll
      ? followUps.edges
      : followUps.edges.slice(0, 5);
    followUpLinks = truncatedFollowUps.map((followUp) => (
      <BlackLink
        key={followUp?.node?.id}
        to={`/${baseUrl}/payment-module/followup-payment-plans/${followUp?.node?.id}`}
      >
        {followUp?.node?.unicefId}
        <br />
      </BlackLink>
    ));
  }

  return (
    <LabelizedField label={t('Related Follow-Up Payment Plans')}>
      <Box display="flex" flexDirection="column">
        {followUpLinks || '-'}
        {followUps?.edges?.length > 5 && (
          <Button
            variant="outlined"
            color="primary"
            onClick={handleButtonClick}
          >
            {showAll ? t('Hide') : t('See all')}
          </Button>
        )}
      </Box>
    </LabelizedField>
  );
}
