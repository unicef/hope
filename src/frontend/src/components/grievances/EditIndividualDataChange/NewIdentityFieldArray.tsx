import { Button, Grid } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { AllAddIndividualFieldsQuery } from '@generated/graphql';
import { AgencyField } from '../AgencyField';
import { removeItemById } from '../utils/helpers';

export interface NewIdentityFieldArrayProps {
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  values;
}

export const NewIdentityFieldArray = ({
  addIndividualFieldsData,
  values,
}: NewIdentityFieldArrayProps): React.ReactElement => {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsIdentities"
        render={(arrayHelpers) => (
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
                  baseName="individualDataUpdateFieldsIdentities"
                  values={values}
                />
              );
            })}

            <Grid item xs={8} />
            <Grid item xs={12}>
              <Button
                color="primary"
                onClick={() => {
                  arrayHelpers.push({
                    id: crypto.randomUUID(),
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
        )}
      />
    </Grid>
  );
};
