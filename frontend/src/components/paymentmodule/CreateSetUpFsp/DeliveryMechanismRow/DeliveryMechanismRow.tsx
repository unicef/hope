import { Box, Grid } from '@mui/material';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { LabelizedField } from '@core/LabelizedField';

interface DeliveryMechanismRowProps {
  index: number;
  step: number;
  values;
  arrayHelpers;
  deliveryMechanismsChoices;
  fspsChoices;
  permissions: string[];
  setFieldValue: (name, value) => void;
}

export function DeliveryMechanismRow({
  index,
  step,
  values,
  deliveryMechanismsChoices,
  fspsChoices,
  setFieldValue,
}: DeliveryMechanismRowProps): React.ReactElement {
  const { t } = useTranslation();
  const chosenFsp = values.deliveryMechanisms[index].fsp;

  const handleFspChange = (e): void => {
    setFieldValue(`deliveryMechanisms[${index}].chosenConfiguration`, '');
    setFieldValue(`deliveryMechanisms[${index}].fsp`, e.target.value);
  };

  return (
    <Box flexDirection="column">
      <Grid alignItems='flex-end' container>
        <Grid item xs={3}>
          <Grid item xs={12}>
            <Box display="flex" alignItems="center">
              {/* <Box mr={4}>{index + 1}</Box> */}
              {step === 0 && deliveryMechanismsChoices && (
                <Field
                  name={`deliveryMechanisms[${index}].deliveryMechanism`}
                  variant="outlined"
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
          <>
            <Grid item xs={3}>
            <Grid item xs={10}>
              <Field
                name={`deliveryMechanisms[${index}].fsp`}
                variant="outlined"
                label={t('FSP')}
                component={FormikSelectField}
                choices={fspsChoices}
                onChange={(e) => handleFspChange(e)}
              />
            </Grid>
          </Grid>
            {fspsChoices.find(el => el.value == chosenFsp)?.configurations.length > 0 && (
            <Grid item xs={3}>
              <Grid item xs={8}>
                <Field
                  name={`deliveryMechanisms[${index}].chosenConfiguration`}
                  variant="outlined"
                  label={t('Configuration')}
                  component={FormikSelectField}
                  choices={
                    fspsChoices.find(el => el.value == chosenFsp)?.configurations
                      ? fspsChoices.find(el => el.value == chosenFsp)?.configurations.map(
                          el => (
                            {
                              name: el.label,
                              value: el.key,
                            }
                          ),
                        )
                      : []
                  }
                />
              </Grid>
            </Grid>
            )}
          </>
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
}
