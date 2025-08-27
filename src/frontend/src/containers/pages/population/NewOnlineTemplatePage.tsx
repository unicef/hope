import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { AuthorizedUsersOnlineListCreate } from '@components/periodicDataUpdates/AuthorizedUsersOnlineListCreate';
import { FieldsToUpdateOnline } from '@components/periodicDataUpdates/FieldsToUpdateOnline';
import { FilterIndividualsOnline } from '@components/periodicDataUpdates/FilterIndividualsOnline';
import { TemplateNameOnline } from '@components/periodicDataUpdates/TemplateNameOnline';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, Step, StepLabel, Stepper } from '@mui/material';
import { PDUOnlineEditCreate } from '@restgenerated/models/PDUOnlineEditCreate';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { Formik } from 'formik';
import moment from 'moment';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

const NewOnlineTemplatePage = (): ReactElement => {
  const { selectedProgram } = useProgramContext();
  const navigate = useNavigate();
  const location = useLocation();
  const [selected, setSelected] = useState<string[]>([]);

  const isPeople = location.pathname.includes('people');
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { mutateAsync: createTemplateMutation } = useMutation({
    mutationFn: (params: {
      businessAreaSlug: string;
      programSlug: string;
      requestBody: PDUOnlineEditCreate;
    }) =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsCreate(
        params,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['periodicFields', businessArea, programId, programId],
      });
      showMessage(t('Template created successfully.'));
      navigate(`/${baseUrl}/population/individuals`, {
        state: { isNewTemplateJustCreated: true },
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage, t('Failed to create template.'));
    },
  });

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

  const [activeStep, setActiveStep] = useState(0);
  const steps = [
    `Filter ${isPeople ? 'People' : beneficiaryGroup?.memberLabelPlural}`,
    'Fields to Update',
    'Authorized Users',
    'Template Name (optional)',
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
    authorizedUsers: [],
    name: '',
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

  // Helper functions
  const yesNoToBoolean = (value) =>
    value === 'YES' ? true : value === 'NO' ? false : null;
  const isEmpty = (value) => {
    if (value == null) return true;
    if (typeof value === 'string') return value.trim() === '';
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') {
      if (Object.keys(value).length === 0) return true;
      if ('from' in value || 'to' in value) return !value.from && !value.to;
    }
    return false;
  };

  const handleSubmit = async (values) => {
    // Build filters object
    const filters = {
      registration_data_import_id:
        filter.registrationDataImportId?.value ?? null,
      target_population_id: filter.targetPopulationId?.value ?? null,
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

    // Remove empty filters
    const filtersToSend = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => !isEmpty(value)),
    );

    // Prepare rounds data
    const roundsDataToSend = values.roundsData
      .filter((el) => checkedFields[el.field])
      .map((data) => ({
        field: data.field,
        round: data.roundNumber,
        round_name: data.roundName,
        id: data.id ?? undefined, // Fix: ensure id is included if present
      }));

    // Prepare payload with camelCase keys
    const payload = {
      roundsData: roundsDataToSend,
      filters: filtersToSend,
      authorizedUsers: values.authorizedUsers,
      name: values.name,
    };

    try {
      await createTemplateMutation({
        businessAreaSlug: businessArea,
        programSlug: programId,
        //@ts-ignore (id not needed in payload)
        requestBody: payload,
      });
    } catch (error) {
      showApiErrorMessages(error, showMessage, t('Failed to create template.'));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={handleSubmit}
      enableReinitialize
    >
      {({ values, setFieldValue, handleSubmit: formikHandleSubmit }) => {
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
          <form onSubmit={formikHandleSubmit}>
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
                <FilterIndividualsOnline
                  isOnPaper={false}
                  filter={filter}
                  setFilter={setFilter}
                />
              )}
              {activeStep === 1 && (
                <FieldsToUpdateOnline
                  values={values}
                  setFieldValue={setFieldValue}
                  checkedFields={checkedFields}
                  setCheckedFields={setCheckedFields}
                />
              )}
              {activeStep === 2 && (
                <AuthorizedUsersOnlineListCreate
                  setFieldValue={setFieldValue}
                  selected={selected}
                  setSelected={setSelected}
                />
              )}
              {activeStep === 3 && (
                <TemplateNameOnline
                  setFieldValue={setFieldValue}
                  value={values.name}
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
                  {activeStep > 0 && activeStep < 4 && (
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
                    {activeStep === 0 && (
                      <Button
                        variant="contained"
                        color="primary"
                        data-cy="next-button"
                        onClick={handleNext}
                      >
                        Next
                      </Button>
                    )}
                    {activeStep === 1 && (
                      <Button
                        variant="contained"
                        color="primary"
                        data-cy="next-button"
                        disabled={roundsDataToSend.length === 0}
                        onClick={handleNext}
                      >
                        Next
                      </Button>
                    )}
                    {activeStep === 2 && (
                      <Button
                        variant="contained"
                        color="primary"
                        data-cy="next-button"
                        onClick={handleNext}
                      >
                        Next
                      </Button>
                    )}
                    {activeStep === 3 && (
                      <Button
                        variant="contained"
                        color="primary"
                        data-cy="submit-button"
                        type="submit"
                      >
                        Generate Template
                      </Button>
                    )}
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
