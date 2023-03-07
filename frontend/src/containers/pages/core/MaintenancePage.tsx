import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Logo } from '../../../components/core/Logo';

export const MaintenancePage = (): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <Box
      display='flex'
      alignItems='center'
      justifyContent='center'
      flexDirection='column'
      style={{ height: '100vh' }}
    >
      <Box mb={4}>
        <Logo transparent={false} displayLogoWithoutSubtitle />
      </Box>
      <Typography align='center' variant='h5'>
        {t(
          'We apologize for the inconvenience, but HOPE is currently undergoing scheduled maintenance.',
        )}
      </Typography>
    </Box>
  );
};
