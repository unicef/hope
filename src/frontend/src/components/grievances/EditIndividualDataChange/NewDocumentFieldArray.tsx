import { Button, Grid2 as Grid } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { AddCircleOutline } from '@mui/icons-material';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { DocumentField } from '../DocumentField';
import { removeItemById } from '../utils/helpers';
import { ReactElement } from 'react';

export interface NewDocumentFieldArrayProps {
  addIndividualFieldsData: any;
  values;
  setFieldValue;
}

export function NewDocumentFieldArray({
  addIndividualFieldsData,
  values,
  setFieldValue,
}: NewDocumentFieldArrayProps): ReactElement {
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
              return (
                <Grid
                  size={{ xs: 12 }}
                  key={`${item?.id}-${item?.country}-${item?.type?.key}`}
                >
                  <DocumentField
                    id={item?.id}
                    onDelete={() =>
                      removeItemById(
                        values.individualDataUpdateFieldsDocuments,
                        item?.id,
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
                </Grid>
              );
            })}

            <Grid size={{ xs: 8 }} />
            <Grid size={{ xs: 12 }}>
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
