import React, { useState } from 'react';
import Button from '@material-ui/core/Button';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { LabelizedField } from '../../../core/LabelizedField';

interface RelatedFollowUpPaymentPlansProps {
  businessArea: string;
  followUps: PaymentPlanQuery['paymentPlan']['followUps'];
}

export const RelatedFollowUpPaymentPlans = ({
  followUps,
  businessArea,
}: RelatedFollowUpPaymentPlansProps): React.ReactElement => {
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
        to={`/${businessArea}/payment-module/payment-plans/${followUp?.node?.id}`}
      >
        {followUp?.node?.unicefId}
      </BlackLink>
    ));
  }

  return (
    <LabelizedField label={t('Related Follow-Up Payment Plans')}>
      {followUpLinks}
      {followUps?.edges?.length > 5 && (
        <Button variant='outlined' color='primary' onClick={handleButtonClick}>
          {showAll ? t('Hide') : t('See all')}
        </Button>
      )}
    </LabelizedField>
  );
};
