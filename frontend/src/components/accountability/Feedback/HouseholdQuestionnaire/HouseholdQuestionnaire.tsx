import { Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { ContentLink } from '../../../core/ContentLink';

interface HouseholdQuestionnaireProps {
  values;
}

export const HouseholdQuestionnaire = ({
  values,
}: HouseholdQuestionnaireProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const selectedHouseholdData = values.selectedHousehold;
  return (
    <Grid container spacing={6}>
      {[
        {
          name: 'size',
          label: t('Household Size'),
          value: selectedHouseholdData.size,
          size: 3,
        },
        {
          name: 'maleChildrenCount',
          label: t('Number of Male Children'),
          value: selectedHouseholdData.maleChildrenCount?.toString(),
          size: 3,
        },
        {
          name: 'femaleChildrenCount',
          label: t('Number of Female Children'),
          value: selectedHouseholdData.femaleChildrenCount?.toString(),
          size: 3,
        },
        {
          name: 'childrenDisabledCount',
          label: t('Number of Disabled Children'),
          value: selectedHouseholdData.childrenDisabledCount?.toString(),
          size: 3,
        },
        {
          name: 'headOfHousehold',
          label: t('Head of Household'),
          value: (
            <ContentLink
              href={`/${businessArea}/population/individuals/${selectedHouseholdData.headOfHousehold.id}`}
            >
              {selectedHouseholdData.headOfHousehold.fullName}
            </ContentLink>
          ),
          size: 3,
        },
        {
          name: 'countryOrigin',
          label: t('Country of Origin'),
          value: selectedHouseholdData.countryOrigin,
          size: 3,
        },
        {
          name: 'address',
          label: t('Address'),
          value: selectedHouseholdData.address,
          size: 3,
        },
        {
          name: 'village',
          label: t('Village'),
          value: selectedHouseholdData.village,
          size: 3,
        },
        {
          name: 'admin1',
          label: t('Administrative Level 1'),
          value: selectedHouseholdData.admin1?.name,
          size: 3,
        },
        {
          name: 'unhcrId',
          label: t('UNHCR CASE ID'),
          value: selectedHouseholdData.unicefId,
          size: 3,
        },
        {
          name: 'months_displaced_h_f',
          label: t('LENGTH OF TIME SINCE ARRIVAL'),
          value: selectedHouseholdData.flexFields?.months_displaced_h_f,
          size: 3,
        },
      ].map((el) => (
        <Grid item xs={3}>
          <Field
            data-cy={`input-${el.name}`}
            name={el.name}
            label={el.label}
            displayValue={el.value || '-'}
            color='primary'
            component={FormikCheckboxField}
          />
        </Grid>
      ))}
    </Grid>
  );
};
