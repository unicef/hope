import { Box, Button, Typography } from '@material-ui/core';
import styled from 'styled-components';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { Title } from '../../../core/Title';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';

const ButtonContainer = styled(Box)`
  width: 200px;
`;

interface AcceptanceProcessProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const AcceptanceProcess = ({
  paymentPlan,
}: AcceptanceProcessProps): React.ReactElement => {
  const { t } = useTranslation();
  const { edges } = paymentPlan.approvalProcess;
  const [showAll, setShowAll] = useState(false);

  const matchDataSize = (data: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges']): PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'] => {
    return showAll ? data : [data[0]];
  };

  if (!edges.length) {
    return null;
  }

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant='h6'>{t('Acceptance Process')}</Typography>
          </Title>
        </Box>
        {matchDataSize(edges).map((edge) => (
          <AcceptanceProcessRow
            key={edge.node.id}
            acceptanceProcess={edge.node}
            paymentPlan={paymentPlan}
          />
        ))}
        {edges.length > 1 && (
          <ButtonContainer>
            <Button
              variant='outlined'
              color='primary'
              onClick={() => setShowAll(!showAll)}
              endIcon={showAll ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {showAll ? t('HIDE') : t('SHOW PREVIOUS')}
            </Button>
          </ButtonContainer>
        )}
      </ContainerColumnWithBorder>
    </Box>
  );
};
