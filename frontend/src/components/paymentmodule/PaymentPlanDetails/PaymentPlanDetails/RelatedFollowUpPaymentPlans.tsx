import { Box } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { cameThroughProgramCycle } from '../../../../utils/utils';
import { BlackLink } from '../../../core/BlackLink';
import { LabelizedField } from '../../../core/LabelizedField';

interface RelatedFollowUpPaymentPlansProps {
  baseUrl: string;
  followUps: PaymentPlanQuery['paymentPlan']['followUps'];
}

export const RelatedFollowUpPaymentPlans = ({
  followUps,
  baseUrl,
}: RelatedFollowUpPaymentPlansProps): React.ReactElement => {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);
  const location = useLocation();

  const handleButtonClick = (): void => {
    setShowAll(!showAll);
  };

  let followUpLinks = null;
  if (followUps?.edges?.length > 0) {
    const truncatedFollowUps = showAll
      ? followUps.edges
      : followUps.edges.slice(0, 5);
    const getDetailsPath = (plan): string => {
      return cameThroughProgramCycle(location)
        ? `/${baseUrl}/payment-module/program-cycles/${plan.programCycle?.id}/followup-payment-plans/${plan.id}`
        : `/${baseUrl}/payment-module/followup-payment-plans/${plan.id}`;
    };

    followUpLinks = truncatedFollowUps.map((followUp) => {
      const detailsPath = getDetailsPath(followUp.node);

      return (
        <BlackLink key={followUp?.node?.id} to={detailsPath}>
          {followUp?.node?.unicefId}
          <br />
        </BlackLink>
      );
    });
  }

  return (
    <LabelizedField label={t('Related Follow-Up Payment Plans')}>
      <Box display='flex' flexDirection='column'>
        {followUpLinks || '-'}
        {followUps?.edges?.length > 5 && (
          <Button
            variant='outlined'
            color='primary'
            onClick={handleButtonClick}
          >
            {showAll ? t('Hide') : t('See all')}
          </Button>
        )}
      </Box>
    </LabelizedField>
  );
};
