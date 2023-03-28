import { Button, Grid } from '@material-ui/core';
import { useLocation } from 'react-router-dom';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';
import { DocumentField } from '../DocumentField';

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
        name='individualDataUpdateFieldsDocuments'
        render={(arrayHelpers) => {
          return (
            <>
              {values.individualDataUpdateFieldsDocuments?.map(
                (item, index) => (
                  <DocumentField
                    index={index}
                    key={`${index}-${item?.country}-${item?.type}`}
                    onDelete={() => arrayHelpers.remove(index)}
                    countryChoices={addIndividualFieldsData.countriesChoices}
                    documentTypeChoices={
                      addIndividualFieldsData.documentTypeChoices
                    }
                    baseName='individualDataUpdateFieldsDocuments'
                    setFieldValue={setFieldValue}
                  />
                ),
              )}

              <Grid item xs={8} />
              <Grid item xs={12}>
                <Button
                  color='primary'
                  disabled={isEditTicket}
                  onClick={() => {
                    arrayHelpers.push({
                      country: null,
                      type: null,
                      number: '',
                    });
                  }}
                  startIcon={<AddCircleOutline />}
                >
                  {t('Add Document')}
                </Button>
              </Grid>
            </>
          );
        }}
      />
    </Grid>
  );
}
