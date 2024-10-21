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
  const { isSocialDctType } = useProgramContext();
  const selectedIndividualData =
    values.selectedIndividual || values.selectedHousehold.headOfHousehold;
  const questionFields = isSocialDctType
    ? [
        {
          name: 'questionnaire_fullName',
          label: t('Individual Full Name'),
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
          name: 'questionnaire_countryOrigin',
          label: t('Country of Origin'),
          value: selectedIndividualData?.countryOrigin,
          size: 3,
        },
        {
          name: 'questionnaire_address',
          label: t('Address'),
          value: selectedIndividualData?.household?.address,
          size: 3,
        },
        {
          name: 'questionnaire_village',
          label: t('Village'),
          value: selectedIndividualData?.household?.village,
          size: 3,
        },
        {
          name: 'questionnaire_adminLevel1',
          label: t('Administrative Level 1'),
          value: selectedIndividualData?.household?.admin1?.name,
          size: 3,
        },
        {
          name: 'questionnaire_adminLevel2',
          label: t('Administrative Level 2'),
          value: selectedIndividualData?.household?.admin2?.name,
          size: 3,
        },
        {
          name: 'questionnaire_adminLevel3',
          label: t('Administrative Level 3'),
          value: selectedIndividualData?.household?.admin3?.name,
          size: 3,
        },
        {
          name: 'questionnaire_adminLevel4',
          label: t('Administrative Level 4'),
          value: selectedIndividualData?.household?.admin4?.name,
          size: 3,
        },
      ]
    : [
        {
          name: 'questionnaire_fullName',
          label: t('Individual Full Name'),
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
          label: t('Relationship to HOH'),
          value: selectedIndividualData.relationship,
          size: 3,
        },
      ];
  return (
    <Grid container spacing={6}>
      {questionFields.map((el) => (
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
