import { Button, Grid } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllAddIndividualFieldsQuery } from '../../__generated__/graphql';
import { DocumentField } from './DocumentField';

const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;

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
                  onClick={() => {
                    arrayHelpers.push({
                      country: null,
                      type: null,
                      number: '',
                    });
                  }}
                >
                  <AddIcon />
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
