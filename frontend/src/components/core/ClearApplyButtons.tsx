import { Box, Button, Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';

interface ClearApplyButtonsProps {
  clearHandler: () => void;
  applyHandler: () => void;
}

export const ClearApplyButtons = ({
  clearHandler,
  applyHandler,
}: ClearApplyButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid container justifyContent='flex-end' spacing={3}>
      <Box mt={4}>
        <Button
          color='primary'
          data-cy='button-filters-clear'
          onClick={() => {
            clearHandler();
          }}
        >
          {t('Clear')}
        </Button>
        <Button
          color='primary'
          variant='outlined'
          data-cy='button-filters-apply'
          onClick={() => applyHandler()}
        >
          {t('Apply')}
        </Button>
      </Box>
    </Grid>
  );
};
