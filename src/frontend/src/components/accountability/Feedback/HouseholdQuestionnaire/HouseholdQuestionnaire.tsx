import { Grid2 as Grid } from '@mui/material';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { ContentLink } from '@core/ContentLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useQuery } from '@tanstack/react-query';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { RestService } from '@restgenerated/services/RestService';

interface HouseholdQuestionnaireProps {
  values;
}

function HouseholdQuestionnaire({
  values,
}: HouseholdQuestionnaireProps): ReactElement {
  const { baseUrl, businessArea, programId, isAllPrograms } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const householdId = values.selectedHousehold?.id;

  const {
    data: household,
    isLoading,
    error,
  } = useQuery<HouseholdDetail>({
    queryKey: ['household', businessArea, householdId, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id: householdId,
        programSlug: programId,
      }),
    enabled: !!householdId && !isAllPrograms,
  });

  const selectedHouseholdData = isAllPrograms
    ? values.selectedHousehold
    : household;

  if (isLoading) return <LoadingComponent />;
  if (error) return <div>Error loading household data</div>;
  if (!selectedHouseholdData) return null;

  return (
    <Grid container spacing={6}>
      {[
        {
          name: 'questionnaire_size',
          label: `${beneficiaryGroup?.groupLabel} Size`,
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
          label: `Head of ${beneficiaryGroup?.groupLabel}`,
          value: (
            <ContentLink
              href={`/${baseUrl}/population/individuals/${selectedHouseholdData.headOfHousehold?.id}`}
            >
              {selectedHouseholdData.headOfHousehold?.fullName}
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
        <Grid key={el.name} size={{ xs: 3 }}>
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
}

export default withErrorBoundary(
  HouseholdQuestionnaire,
  'HouseholdQuestionnaire',
);
