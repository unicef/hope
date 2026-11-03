import { Button } from '@mui/material';
import { AddCircleOutlined } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { AccountField } from '../AccountField';
import { removeItemById } from '../utils/helpers';
import type { ReactElement } from 'react';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { FinancialInstitutionChoice } from '@restgenerated/models/FinancialInstitutionChoice';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

export interface NewAccountFieldArrayProps {
  values;
  individualChoicesData: IndividualChoices;
  accountFinancialInstitutionChoices: FinancialInstitutionChoice[];
}

export function NewAccountFieldArray({
  values,
  individualChoicesData,
  accountFinancialInstitutionChoices,
}: NewAccountFieldArrayProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <ResponsiveGridContainer spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsAccounts"
        render={(arrayHelpers) => (
          <>
            {values.individualDataUpdateFieldsAccounts?.map((item) => {
              const existingOrNewId = item.node?.id || item.id;
              return (
                <AccountField
                  id={existingOrNewId}
                  key={existingOrNewId}
                  onDelete={() =>
                    removeItemById(
                      values.individualDataUpdateFieldsAccounts,
                      existingOrNewId,
                      arrayHelpers,
                    )
                  }
                  baseName="individualDataUpdateFieldsAccounts"
                  values={values}
                  accountTypeChoices={individualChoicesData.accountTypeChoices}
                  accountFinancialInstitutionChoices={
                    accountFinancialInstitutionChoices
                  }
                />
              );
            })}
            <ResponsiveGrid size="twoThirds" />
            <ResponsiveGrid size="full">
              <Button
                color="primary"
                onClick={() => {
                  arrayHelpers.push({
                    id: crypto.randomUUID(),
                  });
                }}
                disabled={isEditTicket}
                startIcon={<AddCircleOutlined />}
              >
                {t('Add Account')}
              </Button>
            </ResponsiveGrid>
          </>
        )}
      />
    </ResponsiveGridContainer>
  );
}
