import { Button } from '@mui/material';
import { AddCircleOutlined } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { AgencyField } from '../AgencyField';
import { removeItemById } from '../utils/helpers';
import type { ReactElement } from 'react';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

export interface NewIdentityFieldArrayProps {
  addIndividualFieldsData: any;
  values;
}

export const NewIdentityFieldArray = ({
  addIndividualFieldsData,
  values,
}: NewIdentityFieldArrayProps): ReactElement => {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const { t } = useTranslation();
  return (
    <ResponsiveGridContainer spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsIdentities"
        render={(arrayHelpers) => (
          <>
            {values.individualDataUpdateFieldsIdentities?.map((item) => {
              return (
                <ResponsiveGrid
                  size="full"
                  key={`${item?.id}-${item?.country}-${item?.partner}`}
                >
                  <AgencyField
                    id={item?.id}
                    onDelete={() =>
                      removeItemById(
                        values.individualDataUpdateFieldsIdentities,
                        item?.id,
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
                </ResponsiveGrid>
              );
            })}

            <ResponsiveGrid size="twoThirds" />
            <ResponsiveGrid size="full">
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
                startIcon={<AddCircleOutlined />}
                disabled={isEditTicket}
              >
                {t('Add Identity')}
              </Button>
            </ResponsiveGrid>
          </>
        )}
      />
    </ResponsiveGridContainer>
  );
};
