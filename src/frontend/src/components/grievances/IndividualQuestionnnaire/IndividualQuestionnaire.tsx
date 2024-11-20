import { Grid } from '@mui/material';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { ContentLink } from '@core/ContentLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

interface IndividualQuestionnaireProps {
  values;
}

export const IndividualQuestionnaire = ({
  values,
}: IndividualQuestionnaireProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const selectedIndividualData =
    values.selectedIndividual || values.selectedHousehold.headOfHousehold;
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <Grid container spacing={6}>
      {[
        {
          name: 'questionnaire_fullName',
          label: `${beneficiaryGroup?.memberLabel} full name`,
          value: (
            <ContentLink
              href={`/${baseUrl}/population/individuals/${selectedIndividualData.id}`}
            >
              {selectedIndividualData.fullName}
            </ContentLink>
          ),
          size: 3,
        },
        {
          name: 'questionnaire_birthDate',
          label: t('Birth Date'),
          value: selectedIndividualData.birthDate,
          size: 3,
        },
        {
          name: 'questionnaire_sex',
          label: t('Gender'),
          value: selectedIndividualData.sex,
          size: 3,
        },
        {
          name: 'questionnaire_phoneNo',
          label: t('Phone Number'),
          value: selectedIndividualData.phoneNo,
          size: 3,
        },
        {
          name: 'questionnaire_relationship',
          label: `Relationship to Head of ${beneficiaryGroup?.groupLabel}`,
          value: selectedIndividualData.relationship,
          size: 3,
        },
      ].map((el) => (
        <Grid key={el.name} item xs={3}>
          <Field
            data-cy={`input-${el.name}`}
            name={el.name}
            label={el.label}
            displayValue={el.value || '-'}
            color="primary"
            component={FormikCheckboxField}
          />
        </Grid>
      ))}
    </Grid>
  );
};
