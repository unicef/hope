import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FieldsToUpdate } from '@components/periodicDataUpdates/FieldsToUpdate';
import { FilterIndividuals } from '@components/periodicDataUpdates/FilterIndividuals';
import { useUploadPeriodicDataUpdateTemplate } from '@components/periodicDataUpdates/PeriodicDataUpdatesTemplatesListActions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, Step, StepLabel, Stepper } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { Formik } from 'formik';
import moment from 'moment';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

const NewOnlineTemplatePage = (): ReactElement => {
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const isPeople = location.pathname.includes('people');
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const initialFilter = {
    registrationDataImportId: null,
    targetPopulationId: null,
    gender: '',
    ageFrom: '',
    ageTo: '',
    registrationDateFrom: '',
    registrationDateTo: '',
    hasGrievanceTicket: '',
    admin1: [],
    admin2: [],
    receivedAssistance: '',
  };

  const [filter, setFilter] = useState(initialFilter);
  const [checkedFields, setCheckedFields] = useState<Record<string, boolean>>(
    {},
  );

  const uploadTemplate = useUploadPeriodicDataUpdateTemplate();

  const [activeStep, setActiveStep] = useState(0);
  const steps = [
    `Filter ${isPeople ? 'People' : beneficiaryGroup?.memberLabelPlural}`,
    'Fields to Update',
  ];

  const { data: periodicFieldsData, isLoading: periodicFieldsLoading } =
    useQuery({
      queryKey: ['periodicFields', businessArea, programId, programId],
      queryFn: () =>
        RestService.restBusinessAreasProgramsPeriodicFieldsList({
          businessAreaSlug: businessArea,
          programSlug: programId,
        }),
    });

  if (periodicFieldsLoading) {
    return <LoadingComponent />;
  }

  if (!periodicFieldsData) {
    return null;
  }

  const mapToInitialValuesRoundsData = (data) => {
    if (!data.results) {
      return [];
    }
    return data.results.map((item) => {
      const { name, pduData, label } = item;
      const { roundsNames, roundsCovered } = pduData;
      const initialRoundNumber = (roundsCovered || 0) + 1;
      return {
        field: name,
        label,
        rounds: roundsNames.map((_, roundIndex) => ({
          round: roundIndex + 1,
          roundName: roundsNames[roundIndex],
        })),
        numberOfRounds: roundsNames.length,
        roundsCovered: roundsCovered || 0,
        roundNumber: initialRoundNumber,
        roundName: roundsNames[initialRoundNumber - 1],
      };
    });
  };

  const mappedRoundsData = mapToInitialValuesRoundsData(periodicFieldsData);

  const initialValues = {
    roundsData: mappedRoundsData,
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: beneficiaryGroup?.memberLabelPlural,
      to: `/${baseUrl}/population/individuals`,
    },
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = (values) => {
    const yesNoToBoolean = (value) => {
      if (value === 'YES') {
        return true;
      }
      if (value === 'NO') {
        return false;
      }
      return null;
    };
    const filters = {
      registration_data_import_id:
        filter.registrationDataImportId?.value || null,
      target_population_id: filter.targetPopulationId?.value || null,
      gender: filter.gender,
      age: {
        from: filter.ageFrom ? Number(filter.ageFrom) : null,
        to: filter.ageTo ? Number(filter.ageTo) : null,
      },
      registration_date: {
        from: filter.registrationDateFrom
          ? moment(filter.registrationDateFrom).format('YYYY-MM-DD')
          : null,
        to: filter.registrationDateTo
          ? moment(filter.registrationDateTo).format('YYYY-MM-DD')
          : null,
      },
      has_grievance_ticket: yesNoToBoolean(filter.hasGrievanceTicket),
      admin1: filter.admin1?.map((el) => el.value),
      admin2: filter.admin2?.map((el) => el.value),
      received_assistance: yesNoToBoolean(filter.receivedAssistance),
    };

    const isEmpty = (value) => {
      return (
        value == null ||
        (typeof value === 'string' && value.trim() === '') ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === 'object' &&
          !Array.isArray(value) &&
          Object.keys(value).length === 0) ||
        (typeof value === 'object' &&
          !Array.isArray(value) &&
          !value.from &&
          !value.to)
      );
    };

    const filtersToSend = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => !isEmpty(value)),
    );

    const roundsDataToSend = values.roundsData
      .filter((el) => checkedFields[el.field] === true)
      .map((data) => ({
        field: data.field,
        round: data.roundNumber,
        round_name: data.roundName,
      }));

    const payload = {
      rounds_data: roundsDataToSend,
      filters: filtersToSend,
    };

    uploadTemplate.mutate(
      {
        businessAreaSlug: businessArea,
        programSlug: programId,
        requestBody: {
          rounds_data: payload.rounds_data,
          filters: payload.filters,
        },
      },
      {
        onSuccess: () => {
          showMessage(t('Template created successfully.'));
          navigate(`/${baseUrl}/population/individuals`, {
            state: { isNewTemplateJustCreated: true },
          });
        },
      },
    );
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={handleSubmit}
      enableReinitialize
    >
      {({ values, setFieldValue, submitForm }) => {
        const roundsDataToSend = values.roundsData
          .filter((el) => checkedFields[el.field] === true)
          .map((data) => ({
            field: data.field,
            rounds: data.rounds
              .filter((round) => round.checked)
              .map((round) => ({
                round: round.round,
                round_name: round.round_name,
              })),
          }));
        return (
          <form onSubmit={handleSubmit}>
            <PageHeader
              title={t('New Online Template Page')}
              breadCrumbs={
                hasPermissions(
                  PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <BaseSection>
              <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((label) => (
                  <Step data-cy="label-key" key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
              {activeStep === 0 && (
                <FilterIndividuals
                  isOnPaper={false}
                  filter={filter}
                  setFilter={setFilter}
                />
              )}
              {activeStep === 1 && (
                <FieldsToUpdate
                  values={values}
                  setFieldValue={setFieldValue}
                  checkedFields={checkedFields}
                  setCheckedFields={setCheckedFields}
                />
              )}
              <Box
                display="flex"
                mt={4}
                justifyContent="flex-start"
                width="100%"
              >
                <Box mr={2}>
                  <Button
                    variant="outlined"
                    color="secondary"
                    component={Link}
                    to={`/${baseUrl}/population/individuals`}
                    data-cy="cancel-button"
                  >
                    Cancel
                  </Button>
                </Box>
                <Box display="flex">
                  {activeStep === 1 && (
                    <Box mr={2}>
                      <Button
                        data-cy="back-button"
                        variant="outlined"
                        onClick={handleBack}
                      >
                        Back
                      </Button>
                    </Box>
                  )}
                  <Box>
                    <Button
                      variant="contained"
                      color="primary"
                      data-cy="submit-button"
                      disabled={
                        activeStep === 1 && roundsDataToSend.length === 0
                      }
                      onClick={activeStep === 1 ? submitForm : handleNext}
                    >
                      {activeStep === 1 ? 'Generate Template' : 'Next'}
                    </Button>
                  </Box>
                </Box>
              </Box>
            </BaseSection>
          </form>
        );
      }}
    </Formik>
  );
};

export default withErrorBoundary(
  NewOnlineTemplatePage,
  'NewOnlineTemplatePage',
);
