import { Button, Grid } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { v4 as uuidv4 } from 'uuid';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';
import { AgencyField } from '../AgencyField';
import { removeItemById } from '../utils/helpers';

export interface NewIdentityFieldArrayProps {
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  values;
}

export function NewIdentityFieldArray({
  addIndividualFieldsData,
  values,
}: NewIdentityFieldArrayProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateFieldsIdentities'
        render={(arrayHelpers) => {
          return (
            <>
              {values.individualDataUpdateFieldsIdentities?.map((item) => {
                const existingOrNewId = item.node?.id || item.id;
                return (
                  <AgencyField
                    id={existingOrNewId}
                    key={`${existingOrNewId}-${item?.country}-${item?.partner}`}
                    onDelete={() =>
                      removeItemById(
                        values.individualDataUpdateFieldsIdentities,
                        existingOrNewId,
                        arrayHelpers,
                      )
                    }
                    countryChoices={addIndividualFieldsData.countriesChoices}
                    identityTypeChoices={
                      addIndividualFieldsData.identityTypeChoices
                    }
                    baseName='individualDataUpdateFieldsIdentities'
                    values={values}
                  />
                );
              })}

              <Grid item xs={8} />
              <Grid item xs={12}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({
                      id: uuidv4(),
                      country: null,
                      partner: null,
                      number: '',
                    });
                  }}
                  startIcon={<AddCircleOutline />}
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
