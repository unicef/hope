import { Grid2 as Grid } from '@mui/material';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { ContentLink } from '@core/ContentLink';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface IndividualQuestionnaireProps {
  values;
}

const IndividualQuestionnaire = ({
  values,
}: IndividualQuestionnaireProps): ReactElement => {
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
          label: t(`${beneficiaryGroup?.memberLabel} Full Name`),
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
          name: 'questionnaire_phoneNo',
          label: t('Phone Number'),
          value: selectedIndividualData.phoneNo,
          size: 3,
        },
        {
          name: 'questionnaire_relationship',
          label: t('Relationship to HOH'),
          value: selectedIndividualData.relationship,
          size: 3,
        },
      ].map((el) => (
        <Grid key={el.name} size={{ xs: 3 }}>
          <Field
            key={el.name}
            name={el.name}
            data-cy={`input-${el.name}`}
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

export default withErrorBoundary(
  IndividualQuestionnaire,
  'IndividualQuestionnaire',
);
