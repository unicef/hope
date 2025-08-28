import withErrorBoundary from '@components/core/withErrorBoundary';
import { replaceLabels } from '@components/grievances/utils/createGrievanceUtils';
import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Box,
  FormHelperText,
  Grid2 as Grid,
  GridSize,
  Typography,
} from '@mui/material';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { FormikAdminAreaAutocomplete } from '@shared/Formik/FormikAdminAreaAutocomplete';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { choicesToDict } from '@utils/utils';
import { Field } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { NewDocumentationFieldArray } from '../../Documentation/NewDocumentationFieldArray';
import { LookUpLinkedTickets } from '../../LookUps/LookUpLinkedTickets/LookUpLinkedTickets';
import { LookUpPaymentRecord } from '../../LookUps/LookUpPaymentRecord/LookUpPaymentRecord';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';

const BoxPadding = styled.div`
  padding: 15px 0;
`;

const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

const BoxWithBorderBottom = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export interface DescriptionProps {
  values;
  showIssueType: (values) => boolean;
  issueTypeToDisplay: string;
  baseUrl: string;
  choicesData: GrievanceChoices;
  programsData: PaginatedProgramListList;
  setFieldValue: (field: string, value, shouldValidate?: boolean) => void;
  errors;
  permissions: string[];
}

function Description({
  values,
  showIssueType,
  issueTypeToDisplay,
  baseUrl,
  choicesData,
  programsData,
  setFieldValue,
  errors,
  permissions,
}: DescriptionProps): ReactElement {
  const { t } = useTranslation();
  const { isAllPrograms, businessArea } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();

  const { data: partnerChoicesData } = useQuery({
    queryKey: ['partnerForGrievanceChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasUsersPartnerForGrievanceChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  // Set program value based on selected household or individual
  useEffect(() => {
    console.log(
      'xdDDDDDDD',
      values.selectedHousehold,
      values.selectedIndividual,
    );
    if (values.selectedIndividual?.program.id) {
      setFieldValue('program', values.selectedIndividual.program.id);
    } else if (values.selectedHousehold?.programId) {
      setFieldValue('program', values.selectedHousehold.programId);
    }
  }, [values.selectedHousehold, values.selectedIndividual, setFieldValue]);
  console.log('values', values);
  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData?.grievanceTicketCategoryChoices || []);
  const priorityChoicesData = choicesData?.grievanceTicketPriorityChoices;
  const urgencyChoicesData = choicesData?.grievanceTicketUrgencyChoices;
  const canAddDocumentation = hasPermissions(
    PERMISSIONS.GRIEVANCE_DOCUMENTS_UPLOAD,
    permissions,
  );
  const canViewHouseholdDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    permissions,
  );
  const canViewIndividualDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
    permissions,
  );

  const mappedProgramChoices = programsData?.results?.map((element) => ({
    name: element.name,
    value: element.id,
  }));

  const isAnonymousTicket =
    !values.selectedHousehold?.id && !values.selectedIndividual?.id;

  return (
    <>
      <BoxPadding>
        <OverviewContainer>
          <Grid container spacing={6}>
            {[
              {
                label: t('Category'),
                value: <span>{categoryChoices[values.category]}</span>,
                size: 4,
              },
              showIssueType(values) && {
                label: t('Issue Type'),
                value: (
                  <span>
                    {replaceLabels(issueTypeToDisplay, beneficiaryGroup)}
                  </span>
                ),
                size: 8,
              },
              {
                label: `${beneficiaryGroup?.groupLabel} ID`,
                value: (
                  <span>
                    {values.selectedHousehold?.id &&
                    canViewHouseholdDetails &&
                    !isAllPrograms ? (
                      <BlackLink
                        to={`/${baseUrl}/population/household/${values.selectedHousehold.id}`}
                      >
                        {values.selectedHousehold.unicefId}
                      </BlackLink>
                    ) : (
                      <div>{values.selectedHousehold?.unicefId || '-'}</div>
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: `${beneficiaryGroup?.memberLabel} ID`,
                value: (
                  <span>
                    {values.selectedIndividual?.id &&
                    canViewIndividualDetails &&
                    !isAllPrograms ? (
                      <BlackLink
                        to={`/${baseUrl}/population/individuals/${values.selectedIndividual.id}`}
                      >
                        {values.selectedIndividual.unicefId}
                      </BlackLink>
                    ) : (
                      <div>{values.selectedIndividual?.unicefId || '-'}</div>
                    )}
                  </span>
                ),
                size: 3,
              },
            ]
              .filter((el) =>
                isSocialDctType ? el.label !== 'Household ID' : el,
              )
              .map((el) => (
                <Grid key={el.label} size={{ xs: el.size as GridSize }}>
                  <LabelizedField label={el.label}>{el.value}</LabelizedField>
                </Grid>
              ))}
          </Grid>
        </OverviewContainer>
        <BoxWithBorderBottom />
        <BoxPadding />
        <Grid container spacing={3}>
          {values.issueType === GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT && (
            <Grid size={{ xs: 3 }}>
              <Field
                name="partner"
                fullWidth
                variant="outlined"
                label={t('Partner*')}
                choices={partnerChoicesData || []}
                component={FormikSelectField}
              />
            </Grid>
          )}
          <Grid size={{ xs: 12 }}>
            <Field
              name="description"
              multiline
              fullWidth
              variant="outlined"
              label={
                values.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD ||
                values.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
                  ? t('Withdrawal Reason*')
                  : t('Description*')
              }
              component={FormikTextField}
            />
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Field
              name="comments"
              multiline
              fullWidth
              variant="outlined"
              label={t('Comments')}
              component={FormikTextField}
            />
          </Grid>
          <Grid size={{ xs: 6 }}>
            <Field
              name="admin"
              variant="outlined"
              component={FormikAdminAreaAutocomplete}
              disabled={Boolean(values.selectedHousehold?.admin2)}
            />
          </Grid>
          <Grid size={{ xs: 6 }}>
            <Field
              name="area"
              fullWidth
              variant="outlined"
              label={t('Area / Village / Pay point')}
              component={FormikTextField}
            />
          </Grid>
          <Grid size={{ xs: 6 }}>
            <Field
              name="language"
              multiline
              fullWidth
              variant="outlined"
              label={t('Languages Spoken')}
              component={FormikTextField}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Field
              name="priority"
              multiline
              fullWidth
              variant="outlined"
              label={t('Priority')}
              choices={priorityChoicesData}
              component={FormikSelectField}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Field
              name="urgency"
              multiline
              fullWidth
              variant="outlined"
              label={t('Urgency')}
              choices={urgencyChoicesData}
              component={FormikSelectField}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Field
              name="program"
              label={t('Programme Name')}
              fullWidth
              variant="outlined"
              choices={mappedProgramChoices}
              component={FormikSelectField}
              disabled={!isAllPrograms || !isAnonymousTicket}
            />
          </Grid>
        </Grid>
        <Box pt={5}>
          <BoxWithBorders>
            <Grid container spacing={4}>
              <Grid size={{ xs: 6 }}>
                <Box py={3}>
                  <LookUpLinkedTickets
                    values={values}
                    onValueChange={setFieldValue}
                  />
                </Box>
              </Grid>
              {(values.issueType === GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT ||
                values.issueType === GRIEVANCE_ISSUE_TYPES.FSP_COMPLAINT) && (
                <Grid size={{ xs: 6 }}>
                  <Box py={3}>
                    <LookUpPaymentRecord
                      values={values}
                      onValueChange={setFieldValue}
                    />
                  </Box>
                  <FormHelperText key="selectedPaymentRecords" error>
                    {errors.selectedPaymentRecords}
                  </FormHelperText>
                </Grid>
              )}
            </Grid>
          </BoxWithBorders>
        </Box>
      </BoxPadding>
      {canAddDocumentation && (
        <Box mt={3}>
          <BoxWithBorderBottom>
            <Title>
              <Typography variant="h6">
                {t(
                  'Grievance Supporting Documents: upload of documents for the ticket',
                )}
              </Typography>
            </Title>
            <NewDocumentationFieldArray
              values={values}
              setFieldValue={setFieldValue}
              errors={errors}
            />
          </BoxWithBorderBottom>
        </Box>
      )}
    </>
  );
}
export default withErrorBoundary(Description, 'Description');
