import { Box } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const WarnIcon = styled(WarningIcon)`
  color: ${({ theme }) => theme.hctPalette.oragne};
`;

interface WarningMissingAmountProps {
  amount: number;
  currency: string;
}

export function WarningMissingAmount({
  amount,
  currency,
}: WarningMissingAmountProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box display='flex' alignItems='center'>
      <WarnIcon />
      {t('Missing')} {amount} {currency}
    </Box>
  );
}
