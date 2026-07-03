import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';
import { Box } from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import Button from '@mui/material/Button';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface RelatedTopUpPaymentPlansProps {
  baseUrl: string;
  topUps: PaymentPlanDetail['topUps'];
}

export function RelatedTopUpPaymentPlans({
  topUps,
  baseUrl,
}: RelatedTopUpPaymentPlansProps): ReactElement {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);

  const handleButtonClick = (): void => {
    setShowAll(!showAll);
  };

  let topUpLinks = null;
  if (topUps?.length > 0) {
    const truncatedTopUps = showAll ? topUps : topUps.slice(0, 5);
    topUpLinks = truncatedTopUps.map((topUp) => (
      <BlackLink
        key={topUp?.id}
        to={`/${baseUrl}/payment-module/top-up-payment-plans/${topUp?.id}`}
      >
        {topUp?.unicefId}
        <br />
      </BlackLink>
    ));
  }

  return (
    <LabelizedField label={t('Related Top-Up Payment Plans')}>
      <Box display="flex" flexDirection="column">
        {topUpLinks || '-'}
        {topUps?.length > 5 && (
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
