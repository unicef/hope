import { Box } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const WarnIcon = styled(WarningIcon)`
  color: ${({ theme }) => theme.hctPalette.orange};
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
    <Box display="flex" alignItems="center">
      <WarnIcon />
      {t('Missing')} {amount} {currency}
    </Box>
  );
}
