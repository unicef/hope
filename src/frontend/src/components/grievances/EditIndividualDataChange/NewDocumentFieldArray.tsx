import { Button, Grid } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { AddCircleOutline } from '@mui/icons-material';
import { FieldArray } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { AllAddIndividualFieldsQuery } from '@generated/graphql';
import { DocumentField } from '../DocumentField';
import { removeItemById } from '../utils/helpers';

export interface NewDocumentFieldArrayProps {
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  values;
  setFieldValue;
}

export function NewDocumentFieldArray({
  addIndividualFieldsData,
  values,
  setFieldValue,
}: NewDocumentFieldArrayProps): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsDocuments"
        render={(arrayHelpers) => (
          <>
            {values.individualDataUpdateFieldsDocuments?.map((item) => {
              const existingOrNewId = item.node?.id || item.id;
              return (
                <DocumentField
                  id={existingOrNewId}
                  key={`${existingOrNewId}-${item?.country}-${item?.type?.key}`}
                  onDelete={() =>
                    removeItemById(
                      values.individualDataUpdateFieldsDocuments,
                      existingOrNewId,
                      arrayHelpers,
                    )
                  }
                  countryChoices={addIndividualFieldsData.countriesChoices}
                  documentTypeChoices={
                    addIndividualFieldsData.documentTypeChoices
                  }
                  baseName="individualDataUpdateFieldsDocuments"
                  setFieldValue={setFieldValue}
                  values={values}
                />
              );
            })}

            <Grid item xs={8} />
            <Grid item xs={12}>
              <Button
                color="primary"
                disabled={isEditTicket}
                onClick={() => {
                  arrayHelpers.push({
                    id: crypto.randomUUID(),
                    country: null,
                    key: null,
                    number: '',
                  });
                }}
                startIcon={<AddCircleOutline />}
              >
                {t('Add Document')}
              </Button>
            </Grid>
          </>
        )}
      />
    </Grid>
  );
}
