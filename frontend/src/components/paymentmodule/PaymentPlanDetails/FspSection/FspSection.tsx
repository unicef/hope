import { Box, Button, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';

interface EntitlementProps {
  businessArea: string;
  permissions: string[];
}

export const FspSection = ({
  businessArea,
  permissions,
}: EntitlementProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box
          display='flex'
          justifyContent='space-between'
          alignItems='center'
          mt={4}
        >
          <Typography variant='h6'>{t('FSPs')}</Typography>
          <Button
            color='primary'
            variant='contained'
            component={Link}
            to={`/${businessArea}/payment-module/payment-plans/${id}/setup-fsp/edit`}
          >
            {t('Set up FSP')}
          </Button>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
};
