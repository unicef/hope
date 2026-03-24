import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { ReactElement } from 'react';

export function TotalAmount(): ReactElement {
  const { t } = useTranslation();

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant="h6">
              {t('Total Amount')}
              {t('per FSP')}
            </Typography>
          </Title>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
}
