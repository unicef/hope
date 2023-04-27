import { Box, Button, IconButton, Typography } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { UniversalMoment } from '../../../core/UniversalMoment';

const StyledBox = styled(Box)`
  background-color: #f4f5f6;
  color: '#49454F';
`;

interface FollowUpItemProps {
  followUp: PaymentPlanQuery['paymentPlan']['followUps'][0];
}

export const FollowUpItem = ({
  followUp,
}: FollowUpItemProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  return (
    <StyledBox
      display='flex'
      alignItems='center'
      flexDirection='column'
      pl={8}
      pr={8}
      pt={4}
      pb={4}
      mt={2}
    >
      <BlackLink
        key={followUp?.node?.id}
        to={`/${businessArea}/payment-module/payment-plans/${followUp?.node?.id}`}
      >
        {t('Follow-up ID:')} {followUp?.node?.unicefId} (
        <UniversalMoment>{followUp?.node?.createdAt}</UniversalMoment>)
      </BlackLink>
      <Typography>{`${followUp?.node?.paymentItems?.totalCount} ${t(
        'Payments',
      )}`}</Typography>
    </StyledBox>
  );
};
