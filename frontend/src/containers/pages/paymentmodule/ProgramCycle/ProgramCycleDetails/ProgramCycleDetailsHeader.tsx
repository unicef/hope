import React from 'react';
import { Box, Button } from '@mui/material';
import { PageHeader } from '@core/PageHeader';
import { ProgramCycle } from '@api/programCycleApi';
import { useTranslation } from 'react-i18next';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';

interface ProgramCycleDetailsHeaderProps {
  programCycle: ProgramCycle;
}

export const ProgramCycleDetailsHeader = ({
  programCycle,
}: ProgramCycleDetailsHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: '..',
    },
  ];

  const finishAction = () => {
    // TODO connect action
    console.log('finish programCycle');
  };

  const buttons = (
    <>
      <Box display="flex" mt={2} mb={2}>
        <Box>
          <Button
            variant="outlined"
            color="primary"
            component={Link}
            startIcon={<AddIcon />}
            to="payment-plans/new-plan"
            data-cy="button-create-payment-plan"
          >
            {t('Create Payment Plan')}
          </Button>
        </Box>
        <Box ml={2}>
          <Button
            variant="contained"
            color="primary"
            onClick={finishAction}
            data-cy="button-create-payment-plan"
          >
            {t('Finish Cycle')}
          </Button>
        </Box>
      </Box>
    </>
  );

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems={'center'}>
          <Box display="flex" flexDirection="column">
            <Box>
              {programCycle.title} (ID: {programCycle.unicef_id})
            </Box>
          </Box>
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
    >
      {buttons}
    </PageHeader>
  );
};
