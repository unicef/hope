import styled from 'styled-components';
import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';

const GreyText = styled.div`
  color: #9e9e9e;
`;

interface FspRowProps {
  fsp;
}

export function FspRow({ fsp }: FspRowProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box display='flex' alignItems='center'>
      {fsp.name}
      <GreyText>
        {' '}
        | {t('Total Maximum Amount')}: {fsp.maxAmount} | {fsp.deliveryMechanism}
      </GreyText>
    </Box>
  );
}
