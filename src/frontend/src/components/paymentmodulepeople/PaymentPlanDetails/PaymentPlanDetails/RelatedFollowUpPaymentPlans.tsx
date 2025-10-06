import { ReactElement, useState } from 'react';
import Button from '@mui/material/Button';
import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface RelatedFollowUpPaymentPlansProps {
  baseUrl: string;
  followUps: PaymentPlanDetail['followUps'];
}

export function RelatedFollowUpPaymentPlans({
  followUps,
  baseUrl,
}: RelatedFollowUpPaymentPlansProps): ReactElement {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);

  const handleButtonClick = (): void => {
    setShowAll(!showAll);
  };

  let followUpLinks = null;
  if (followUps?.length > 0) {
    const truncatedFollowUps = showAll ? followUps : followUps.slice(0, 5);
    followUpLinks = truncatedFollowUps.map((followUp) => (
      <BlackLink
        key={followUp?.id}
        to={`/${baseUrl}/payment-module/followup-payment-plans/${followUp?.id}`}
      >
        {followUp?.unicefId}
        <br />
      </BlackLink>
    ));
  }

  return (
    <LabelizedField label={t('Related Follow-Up Payment Plans')}>
      <Box display="flex" flexDirection="column">
        {followUpLinks || '-'}
        {followUps?.length > 5 && (
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
