import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { Title } from '../../../core/Title';

export function TotalAmount(): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant='h6'>
              {t('Total Amount')}(PLN) {t('per FSP')}
            </Typography>
          </Title>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
}
