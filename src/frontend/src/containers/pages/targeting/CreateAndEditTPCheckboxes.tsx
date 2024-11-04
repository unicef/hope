import React from 'react';
import { Box, Grid } from '@mui/material';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';

interface CreateAndEditTPCheckboxesProps {
  isStandardDctType: boolean;
  isSocialDctType: boolean;
  screenBeneficiary: boolean;
}

export const CreateAndEditTPCheckboxes: React.FC<
  CreateAndEditTPCheckboxesProps
> = ({ isStandardDctType, isSocialDctType, screenBeneficiary }) => {
  const { t } = useTranslation();

  return (
    <Box mt={3} p={3}>
      <Grid container spacing={3}>
        {isStandardDctType && (
          <Grid item xs={6}>
            <Field
              name="flagExcludeIfActiveAdjudicationTicket"
              label={t('Exclude Households with Active Adjudication Ticket')}
              color="primary"
              component={FormikCheckboxField}
              data-cy="input-active-households-adjudication-ticket"
            />
          </Grid>
        )}
        {isSocialDctType && (
          <Grid item xs={6}>
            <Field
              name="flagExcludeIfActiveAdjudicationTicket"
              label={t('Exclude People with Active Adjudication Ticket')}
              color="primary"
              component={FormikCheckboxField}
              data-cy="input-active-people-adjudication-ticket"
            />
          </Grid>
        )}
        {screenBeneficiary && isSocialDctType && (
          <Grid item xs={6}>
            <Field
              name="flagExcludeIfOnSanctionList"
              label={t('Exclude People with an Active Sanction Screen Flag')}
              color="primary"
              component={FormikCheckboxField}
              data-cy="input-active-people-sanction-flag"
            />
          </Grid>
        )}
        {screenBeneficiary && isStandardDctType && (
          <Grid item xs={6}>
            <Field
              name="flagExcludeIfOnSanctionList"
              label={t(
                'Exclude Households with an Active Sanction Screen Flag',
              )}
              color="primary"
              component={FormikCheckboxField}
              data-cy="input-active-sanction-flag"
            />
          </Grid>
        )}
      </Grid>
    </Box>
  );
};
