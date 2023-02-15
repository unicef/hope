import { Box, Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { LabelizedField } from '../../../core/LabelizedField';

interface DeliveryMechanismRowProps {
  index: number;
  step: number;
  values;
  arrayHelpers;
  deliveryMechanismsChoices;
  fspsChoices;
  permissions: string[];
}

export const DeliveryMechanismRow = ({
  index,
  step,
  values,
  deliveryMechanismsChoices,
  fspsChoices,
}: DeliveryMechanismRowProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Box flexDirection='column'>
      <Grid container>
        <Grid item xs={3}>
          <Grid item xs={12}>
            <Box display='flex' alignItems='center'>
              {/* <Box mr={4}>{index + 1}</Box> */}
              {step === 0 && deliveryMechanismsChoices && (
                <Field
                  name={`deliveryMechanisms[${index}].deliveryMechanism`}
                  variant='outlined'
                  label={t('Delivery Mechanism')}
                  component={FormikSelectField}
                  choices={deliveryMechanismsChoices}
                />
              )}
              {step === 1 && (
                <LabelizedField
                  label={t('Delivery Mechanism')}
                  value={values.deliveryMechanisms[index].deliveryMechanism}
                />
              )}
            </Box>
          </Grid>
        </Grid>
        {step === 1 && fspsChoices && (
          <Grid item xs={3}>
            <Grid item xs={8}>
              <Field
                name={`deliveryMechanisms[${index}].fsp`}
                variant='outlined'
                label={t('FSP')}
                component={FormikSelectField}
                choices={fspsChoices}
              />
            </Grid>
          </Grid>
        )}
        {/* {step === 0 && values.deliveryMechanisms[index].deliveryMechanism && (
          <Grid item xs={3}>
            {hasPermissions(
              PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
              permissions,
            ) ? (
              <IconButton onClick={() => arrayHelpers.remove(index)}>
                <Delete />
              </IconButton>
            ) : null}
          </Grid>
        )} */}
      </Grid>
    </Box>
  );
};
