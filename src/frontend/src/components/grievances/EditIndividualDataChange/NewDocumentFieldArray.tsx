import { Button } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { AddCircleOutlined } from '@mui/icons-material';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { DocumentField } from '../DocumentField';
import { removeItemById } from '../utils/helpers';
import type { ReactElement } from 'react';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

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
    <ResponsiveGridContainer spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsDocuments"
        render={(arrayHelpers) => (
          <>
            {values.individualDataUpdateFieldsDocuments?.map((item) => {
              return (
                <ResponsiveGrid
                  size="full"
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
                </ResponsiveGrid>
              );
            })}

            <ResponsiveGrid size="twoThirds" />
            <ResponsiveGrid size="full">
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
                startIcon={<AddCircleOutlined />}
              >
                {t('Add Document')}
              </Button>
            </ResponsiveGrid>
          </>
        )}
      />
    </ResponsiveGridContainer>
  );
}
