import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/EditProgram/DetailsStep';
import { PartnersStep } from '@components/programs/EditProgram/PartnersStep';
import { ProgramFieldSeriesStep } from '@components/programs/EditProgram/ProgramFieldSeriesStep';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';
import {
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  usePduSubtypeChoicesDataQuery,
  useUpdateProgramMutation,
  useUpdateProgramPartnersMutation,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Fade } from '@mui/material';
import {
  decodeIdString,
  mapPartnerChoicesWithoutUnicef,
  isPartnerVisible,
} from '@utils/utils';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { hasPermissionInModule } from '../../../config/permissions';
import {
  editPartnersValidationSchema,
  editProgramDetailsValidationSchema,
} from '@components/programs/CreateProgram/editProgramValidationSchema';
import { omit } from 'lodash';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

const EditProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const location = useLocation();
  const option = location.state?.option;

  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });

  const { data: program, isLoading: loadingProgram } = useQuery({
    queryKey: ['businessAreaProgram', businessArea, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        slug: id,
      }),
  });

  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const { data: pdusubtypeChoicesData, loading: pdusubtypeChoicesLoading } =
    usePduSubtypeChoicesDataQuery();

  const [updateProgramDetails, { loading: loadingUpdate }] =
    useUpdateProgramMutation({
      refetchQueries: [
        {
          query: ALL_LOG_ENTRIES_QUERY,
          variables: {
            objectId: decodeIdString(id),
            count: 5,
            businessArea,
          },
        },
      ],
    });

  const [updateProgramPartners] = useUpdateProgramPartnersMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(id),
          count: 5,
          businessArea,
        },
      },
    ],
  });

  if (
    loadingProgram ||
    treeLoading ||
    userPartnerChoicesLoading ||
    pdusubtypeChoicesLoading
  )
    return <LoadingComponent />;

  if (
    !program ||
    !treeData ||
    !userPartnerChoicesData ||
    !pdusubtypeChoicesData
  )
    return null;

  const {
    name,
    programme_code,
    start_date,
    end_date,
    sector,
    data_collecting_type,
    beneficiary_group,
    description,
    budget = '',
    administrative_areas_of_implementation,
    population_goal = '',
    cash_plus = false,
    frequency_of_payments = 'REGULAR',
    version,
    partners,
    partner_access = ProgramPartnerAccess.AllPartnersAccess,
    registration_imports,
    pdu_fields,
    target_populations_count,
  } = program;

  const programHasRdi = registration_imports?.total_count > 0;
  const programHasTp = target_populations_count > 0;

  const handleSubmitProgramDetails = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : 0;
    const population_goalValue = parseInt(values.population_goal, 10) ?? 0;
    const population_goalParsed = !Number.isNaN(population_goalValue)
      ? population_goalValue
      : 0;

    const pduFieldsToSend = values.pduFields
      .filter((item) => item.label !== '')
      .map(({ pduData, ...rest }) => ({
        ...rest,
        pduData: pduData
          ? {
              ...Object.fromEntries(
                Object.entries(pduData).filter(
                  ([key]) => key !== '__typename' && key !== 'id',
                ),
              ),
              roundsNames: (() => {
                if (!pduData.roundsNames) {
                  pduData.roundsNames = [];
                }

                if (
                  pduData.numberOfRounds === 1 &&
                  pduData.roundsNames.length === 0
                ) {
                  return [''];
                }

                return pduData.roundsNames.map((roundName) => roundName || '');
              })(),
            }
          : pduData,
      }));

    try {
      const requestValuesDetails = omit(values, [
        'editMode',
        'partners',
        'partnerAccess',
        'pduFields',
      ]);
      const response = await updateProgramDetails({
        variables: {
          programData: {
            id,
            ...requestValuesDetails,
            budget: budgetToFixed,
            population_goal: population_goalParsed,
            pduFields: pduFieldsToSend,
          },
          version,
        },
      });
      showMessage(t('Programme edited.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleSubmitPartners = async (values): Promise<void> => {
    const partnersToSet =
      values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];

    try {
      const response = await updateProgramPartners({
        variables: {
          programData: {
            id,
            partners: partnersToSet,
            partnerAccess: values.partnerAccess,
          },
          version,
        },
      });
      showMessage(t('Programme Partners updated.'));
      navigate(
        `/${baseUrl}/details/${response.data.updateProgramPartners.program.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const mappedPduFields = Object.entries(pdu_fields).map(([, field]) => {
    const { ...rest } = field;
    return {
      ...rest,
      label: JSON.parse(field.label)['English(EN)'],
    };
  });

  const initialValuesProgramDetails = {
    editMode: true,
    name,
    programmeCode: programme_code,
    startDate: start_date,
    endDate: end_date,
    sector,
    dataCollectingTypeCode: data_collecting_type.code,
    beneficiaryGroup: decodeIdString(beneficiary_group.id),
    description,
    budget,
    administrativeAreasOfImplementation: administrative_areas_of_implementation,
    populationGoal: population_goal,
    cashPlus: cash_plus,
    frequencyOfPayments: frequency_of_payments,
    pduFields: pdu_fields,
  };

  initialValuesProgramDetails.budget =
    program.budget === '0.00' ? '' : program.budget;
  initialValuesProgramDetails.populationGoal =
    program.population_goal === 0 ? '' : program.population_goal;

  const initialValuesPartners = {
    partners:
      partners.length > 0
        ? partners
            .filter((partner) => isPartnerVisible(partner.name))
            .map((partner) => ({
              id: partner.id,
              areas: partner.areas.map((area) => decodeIdString(area.id)),
              areaAccess: partner.areaAccess,
            }))
        : [],
    partner_access,
  };

  const stepFields = [
    [
      'name',
      'programmeCode',
      'startDate',
      'endDate',
      'sector',
      'dataCollectingTypeCode',
      'beneficiaryGroup',
      'description',
      'budget',
      'administrativeAreasOfImplementation',
      'population_goal',
      'cashPlus',
      'frequencyOfPayments',
    ],
    ['partnerAccess'],
  ];

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme'),
      to: `/${baseUrl}/details/${id}`,
    },
  ];
  const stepsData = [
    {
      title: t('Details'),
      description: t(
        'To create a new Programme, please complete all required fields on the form below and save.',
      ),
      dataCy: 'step-button-details',
    },
    {
      title: t('Programme Time Series Fields'),
      description: t(
        'The Time Series Fields feature allows serial updating of individual data through an XLSX file.',
      ),
      dataCy: 'step-button-time-series-fields',
    },
  ];

  return (
    <>
      <PageHeader
        title={`${t('Edit Programme')}: (${name})`}
        breadCrumbs={
          hasPermissionInModule('PROGRAMME_VIEW_LIST_AND_DETAILS', permissions)
            ? breadCrumbsItems
            : null
        }
      />
      {option === 'details' && (
        <Formik
          initialValues={initialValuesProgramDetails}
          onSubmit={(values) => {
            handleSubmitProgramDetails(values);
          }}
          validationSchema={editProgramDetailsValidationSchema(
            t,
            initialValuesProgramDetails,
          )}
          validateOnChange={true}
        >
          {({
            submitForm,
            values,
            validateForm,
            setFieldTouched,
            setFieldValue,
            errors,
            setErrors,
          }) => {
            const handleNextStep = async () => {
              await handleNext({
                validateForm,
                stepFields,
                step,
                setStep,
                setFieldTouched,
                values,
                setErrors,
              });
            };
            return (
              <BaseSection
                title={stepsData[step].title}
                description={stepsData[step].description}
                stepper={
                  <ProgramStepper
                    step={step}
                    setStep={setStep}
                    stepsData={stepsData}
                  />
                }
              >
                <Box p={3}>
                  <>
                    <Fade in={step === 0} timeout={600}>
                      <div>
                        {step === 0 && (
                          <DetailsStep
                            values={values}
                            handleNext={handleNextStep}
                            programId={id}
                            errors={errors}
                            programHasRdi={programHasRdi}
                          />
                        )}
                      </div>
                    </Fade>
                    <Fade in={step === 1} timeout={600}>
                      <div>
                        {step === 1 && (
                          <ProgramFieldSeriesStep
                            values={values}
                            step={step}
                            setStep={setStep}
                            pdusubtypeChoicesData={pdusubtypeChoicesData}
                            programHasRdi={programHasRdi}
                            programHasTp={programHasTp}
                            programId={id}
                            program={program}
                            setFieldValue={setFieldValue}
                            submitForm={submitForm}
                          />
                        )}
                      </div>
                    </Fade>
                  </>
                </Box>
              </BaseSection>
            );
          }}
        </Formik>
      )}
      {option === 'partners' && (
        <Formik
          initialValues={initialValuesPartners}
          onSubmit={(values) => {
            handleSubmitPartners(values);
          }}
          validationSchema={editPartnersValidationSchema(t)}
        >
          {({ submitForm, values, setFieldValue }) => {
            const mappedPartnerChoices = mapPartnerChoicesWithoutUnicef(
              userPartnerChoices,
              values.partners,
            );

            return (
              <BaseSection title={t('Programme Partners')}>
                <Fade in={option === 'partners'} timeout={600}>
                  <div>
                    <PartnersStep
                      values={values}
                      allAreasTreeData={allAreasTree}
                      partnerChoices={mappedPartnerChoices}
                      submitForm={submitForm}
                      setFieldValue={setFieldValue}
                      programId={id}
                      loading={loadingUpdate}
                    />
                  </div>
                </Fade>
              </BaseSection>
            );
          }}
        </Formik>
      )}
    </>
  );
};
export default withErrorBoundary(EditProgramPage, 'EditProgramPage');
