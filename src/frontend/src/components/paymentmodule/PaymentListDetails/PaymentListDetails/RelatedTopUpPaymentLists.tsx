import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';
import { Box } from '@mui/material';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import Button from '@mui/material/Button';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface RelatedTopUpPaymentListsProps {
  baseUrl: string;
  topUps: PaymentListDetail['topUps'];
}

export function RelatedTopUpPaymentLists({
  topUps,
  baseUrl,
}: RelatedTopUpPaymentListsProps): ReactElement {
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
        to={`/${baseUrl}/payment-module/top-up-payment-lists/${topUp?.id}`}
      >
        {topUp?.unicefId}
        <br />
      </BlackLink>
    ));
  }

  return (
    <LabelizedField label={t('Related Top-Up Payment Lists')}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
        }}
      >
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
