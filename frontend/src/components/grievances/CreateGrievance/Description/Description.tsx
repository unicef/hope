import {
  Box,
  FormHelperText,
  Grid,
  GridSize,
  Typography,
} from '@material-ui/core';
import { Field } from 'formik';
import styled from 'styled-components';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikAdminAreaAutocomplete } from '../../../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { GRIEVANCE_ISSUE_TYPES } from '../../../../utils/constants';
import { reduceChoices } from '../../../../utils/utils';
import {
  GrievancesChoiceDataQuery,
  UserChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { ContentLink } from '../../../core/ContentLink';
import { LabelizedField } from '../../../core/LabelizedField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { NewDocumentationFieldArray } from '../../Documentation/NewDocumentationFieldArray';
import { LookUpPaymentRecord } from '../../LookUps/LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpRelatedTickets } from '../../LookUps/LookUpRelatedTickets/LookUpRelatedTickets';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { Title } from '../../../core/Title';

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
  selectedIssueType: (values) => string;
  businessArea: string;
  choicesData: GrievancesChoiceDataQuery;
  userChoices: UserChoiceDataQuery;
  mappedPrograms: {
    name: string;
    value: string;
  }[];
  setFieldValue: (field: string, value, shouldValidate?: boolean) => void;
  errors;
  permissions: string[];
}

export const Description = ({
  values,
  showIssueType,
  selectedIssueType,
  businessArea,
  choicesData,
  userChoices,
  mappedPrograms,
  setFieldValue,
  errors,
  permissions,
}: DescriptionProps): React.ReactElement => {
  const { t } = useTranslation();
  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData?.grievanceTicketCategoryChoices || []);
  const priorityChoicesData = choicesData?.grievanceTicketPriorityChoices;
  const urgencyChoicesData = choicesData?.grievanceTicketUrgencyChoices;
  const canAddDocumentation = hasPermissions(
    PERMISSIONS.GRIEVANCE_DOCUMENTS_UPLOAD,
    permissions,
  );

  return (
    <>
      <BoxPadding>
        <OverviewContainer>
          <Grid container spacing={6}>
            {[
              {
                label: t('Category'),
                value: <span>{categoryChoices[values.category]}</span>,
                size: 3,
              },
              showIssueType(values) && {
                label: t('Issue Type'),
                value: <span>{selectedIssueType(values)}</span>,
                size: 9,
              },
              {
                label: t('HOUSEHOLD ID'),
                value: (
                  <span>
                    {values.selectedHousehold?.id ? (
                      <ContentLink
                        href={`/${businessArea}/population/household/${values.selectedHousehold.id}`}
                      >
                        {values.selectedHousehold.unicefId}
                      </ContentLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('INDIVIDUAL ID'),
                value: (
                  <span>
                    {values.selectedIndividual?.id ? (
                      <ContentLink
                        href={`/${businessArea}/population/individuals/${values.selectedIndividual.id}`}
                      >
                        {values.selectedIndividual.unicefId}
                      </ContentLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: 3,
              },
            ]
              .filter((el) => el)
              .map((el) => (
                <Grid key={el.label} item xs={el.size as GridSize}>
                  <LabelizedField label={el.label}>{el.value}</LabelizedField>
                </Grid>
              ))}
          </Grid>
        </OverviewContainer>
        <BoxWithBorderBottom />
        <BoxPadding />
        <Grid container spacing={3}>
          {values.issueType === GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT && (
            <Grid item xs={3}>
              <Field
                name='partner'
                fullWidth
                variant='outlined'
                label={t('Partner*')}
                choices={userChoices.userPartnerChoices}
                component={FormikSelectField}
              />
            </Grid>
          )}
          <Grid item xs={12}>
            <Field
              name='description'
              multiline
              fullWidth
              variant='outlined'
              label={
                values.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD ||
                values.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
                  ? t('Withdrawal Reason*')
                  : t('Description*')
              }
              component={FormikTextField}
            />
          </Grid>
          <Grid item xs={12}>
            <Field
              name='comments'
              multiline
              fullWidth
              variant='outlined'
              label={t('Comments')}
              component={FormikTextField}
            />
          </Grid>
          <Grid item xs={6}>
            <Field
              name='admin'
              label={t('Administrative Level 2')}
              variant='outlined'
              component={FormikAdminAreaAutocomplete}
            />
          </Grid>
          <Grid item xs={6}>
            <Field
              name='area'
              fullWidth
              variant='outlined'
              label={t('Area / Village / Pay point')}
              component={FormikTextField}
            />
          </Grid>
          <Grid item xs={6}>
            <Field
              name='language'
              multiline
              fullWidth
              variant='outlined'
              label={t('Languages Spoken')}
              component={FormikTextField}
            />
          </Grid>
          <Grid item xs={3}>
            <Field
              name='priority'
              multiline
              fullWidth
              variant='outlined'
              label={t('Priority')}
              choices={priorityChoicesData}
              component={FormikSelectField}
            />
          </Grid>
          <Grid item xs={3}>
            <Field
              name='urgency'
              multiline
              fullWidth
              variant='outlined'
              label={t('Urgency')}
              choices={urgencyChoicesData}
              component={FormikSelectField}
            />
          </Grid>
          {+values.issueType !== +GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL && (
            <Grid item xs={6}>
              <Field
                name='programme'
                fullWidth
                variant='outlined'
                label={t('Programme Title')}
                choices={mappedPrograms}
                component={FormikSelectField}
              />
            </Grid>
          )}
        </Grid>
        <Box pt={5}>
          <BoxWithBorders>
            <Grid container spacing={4}>
              <Grid item xs={6}>
                <Box py={3}>
                  <LookUpRelatedTickets
                    values={values}
                    onValueChange={setFieldValue}
                  />
                </Box>
              </Grid>
              {(values.issueType === GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT ||
                values.issueType === GRIEVANCE_ISSUE_TYPES.FSP_COMPLAINT) && (
                <Grid item xs={6}>
                  <Box py={3}>
                    <LookUpPaymentRecord
                      values={values}
                      onValueChange={setFieldValue}
                    />
                  </Box>
                  <FormHelperText key='selectedPaymentRecords' error>
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
          <Title>
            <Typography variant='h6'>{t('Documentation')}</Typography>
          </Title>
          <NewDocumentationFieldArray
            values={values}
            setFieldValue={setFieldValue}
            errors={errors}
          />
        </Box>
      )}
    </>
  );
};
