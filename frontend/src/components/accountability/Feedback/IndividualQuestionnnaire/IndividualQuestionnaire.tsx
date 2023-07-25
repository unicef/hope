import { Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { ContentLink } from '../../../core/ContentLink';

interface IndividualQuestionnaireProps {
  values;
}

export const IndividualQuestionnaire = ({
  values,
}: IndividualQuestionnaireProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea;
  const selectedIndividualData =
    values.selectedIndividual || values.selectedHousehold.headOfHousehold;
  return (
    <Grid container spacing={6}>
      {[
        {
          name: 'fullName',
          label: t('Individual Full Name'),
          value: (
            <ContentLink
              href={`/${businessArea}/population/individuals/${selectedIndividualData.id}`}
            >
              {selectedIndividualData.fullName}
            </ContentLink>
          ),
          size: 3,
        },
        {
          name: 'birthDate',
          label: t('Birth Date'),
          value: selectedIndividualData.birthDate,
          size: 3,
        },
        {
          name: 'phoneNo',
          label: t('Phone Number'),
          value: selectedIndividualData.phoneNo,
          size: 3,
        },
        {
          name: 'relationship',
          label: t('Relationship to HOH'),
          value: selectedIndividualData.relationship,
          size: 3,
        },
      ].map((el) => (
        <Grid item xs={3}>
          <Field
            name={el.name}
            data-cy={`input-${el.name}`}
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
