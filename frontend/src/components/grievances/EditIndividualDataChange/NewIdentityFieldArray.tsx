import { Button, Grid } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';
import { AgencyField } from '../AgencyField';

export interface NewIdentityFieldArrayProps {
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  values;
}

export function NewIdentityFieldArray({
  addIndividualFieldsData,
  values,
}: NewIdentityFieldArrayProps): React.ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateFieldsIdentities'
        render={(arrayHelpers) => {
          return (
            <>
              {values.individualDataUpdateFieldsIdentities?.map(
                (item, index) => (
                  <AgencyField
                    index={index}
                    key={`${index}-${item?.country}-${item?.partner}`}
                    onDelete={() => arrayHelpers.remove(index)}
                    countryChoices={addIndividualFieldsData.countriesChoices}
                    identityTypeChoices={
                      addIndividualFieldsData.identityTypeChoices
                    }
                    baseName='individualDataUpdateFieldsIdentities'
                  />
                ),
              )}

              <Grid item xs={8} />
              <Grid item xs={12}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({
                      country: null,
                      partner: null,
                      number: '',
                    });
                  }}
                  startIcon={<AddCircleOutline />}
                  disabled={isEditTicket}
                >
                  {t('Add Identity')}
                </Button>
              </Grid>
            </>
          );
        }}
      />
    </Grid>
  );
}
