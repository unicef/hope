import { Grid } from '@mui/material';
import { Field } from 'formik';
import * as React from 'react';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { ContentLink } from '@core/ContentLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AllHouseholdsQuery, useHouseholdLazyQuery } from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';

interface HouseholdQuestionnaireProps {
  values;
}

export function HouseholdQuestionnaire({
  values,
}: HouseholdQuestionnaireProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'] =
    values.selectedHousehold;
  const [getHousehold, { data: fullHousehold, loading: fullHouseholdLoading }] =
    useHouseholdLazyQuery({ variables: { id: household?.id } });

  useEffect(() => {
    if (values.selectedHousehold) {
      getHousehold();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [values.selectedHousehold]);

  if (!fullHousehold) return null;
  if (fullHouseholdLoading) return <LoadingComponent />;

  const selectedHouseholdData = fullHousehold?.household;

  return (
    <Grid container spacing={6}>
      {[
        {
          name: 'questionnaire_size',
          label: t('Household Size'),
          value: selectedHouseholdData.size,
          size: 3,
        },
        {
          name: 'questionnaire_maleChildrenCount',
          label: t('Number of Male Children'),
          value: selectedHouseholdData.maleChildrenCount?.toString(),
          size: 3,
        },
        {
          name: 'questionnaire_femaleChildrenCount',
          label: t('Number of Female Children'),
          value: selectedHouseholdData.femaleChildrenCount?.toString(),
          size: 3,
        },
        {
          name: 'questionnaire_childrenDisabledCount',
          label: t('Number of Disabled Children'),
          value: selectedHouseholdData.childrenDisabledCount?.toString(),
          size: 3,
        },
        {
          name: 'questionnaire_headOfHousehold',
          label: t('Head of Household'),
          value: (
            <ContentLink
              href={`/${baseUrl}/population/individuals/${selectedHouseholdData.headOfHousehold.id}`}
            >
              {selectedHouseholdData.headOfHousehold.fullName}
            </ContentLink>
          ),
          size: 3,
        },
        {
          name: 'questionnaire_countryOrigin',
          label: t('Country of Origin'),
          value: selectedHouseholdData.countryOrigin,
          size: 3,
        },
        {
          name: 'questionnaire_address',
          label: t('Address'),
          value: selectedHouseholdData.address,
          size: 3,
        },
        {
          name: 'questionnaire_village',
          label: t('Village'),
          value: selectedHouseholdData.village,
          size: 3,
        },
        {
          name: 'questionnaire_admin1',
          label: t('Administrative Level 1'),
          value: selectedHouseholdData.admin1?.name,
          size: 3,
        },
        {
          name: 'questionnaire_admin2',
          label: t('Administrative Level 2'),
          value: selectedHouseholdData.admin2?.name,
          size: 3,
        },
        {
          name: 'questionnaire_admin3',
          label: t('Administrative Level 3'),
          value: selectedHouseholdData.admin3?.name,
          size: 3,
        },
        {
          name: 'questionnaire_admin4',
          label: t('Administrative Level 4'),
          value: selectedHouseholdData.admin4?.name,
          size: 3,
        },
        {
          name: 'questionnaire_months_displaced_h_f',
          label: t('LENGTH OF TIME SINCE ARRIVAL'),
          value: selectedHouseholdData.flexFields?.months_displaced_h_f,
          size: 3,
        },
      ].map((el) => (
        <Grid key={el.name} item xs={3}>
          <Field
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
}
