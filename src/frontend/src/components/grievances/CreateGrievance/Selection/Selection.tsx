import { Grid } from '@mui/material';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { GrievancesChoiceDataQuery } from '@generated/graphql';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { useProgramContext } from 'src/programContext';
import {
  getGrievanceCategoryDescriptions,
  getGrievanceIssueTypeDescriptions,
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
} from '@utils/constants';

export interface SelectionProps {
  handleChange: (e: React.ChangeEvent) => void;
  choicesData: GrievancesChoiceDataQuery;
  setFieldValue: (field: string, value, shouldValidate?: boolean) => void;
  showIssueType: (values) => boolean;
  values;
  redirectedFromRelatedTicket: boolean;
}

export function Selection({
  handleChange,
  choicesData,
  setFieldValue,
  showIssueType,
  values,
  redirectedFromRelatedTicket,
}: SelectionProps): React.ReactElement {
  const { t } = useTranslation();
  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const dataChangeIssueTypes = [
    { name: `${beneficiaryGroup?.groupLabel} Data Update`, value: '13' },
    { name: `${beneficiaryGroup?.memberLabel} Data Update`, value: '14' },
  ];

  const categoryDescriptions =
    getGrievanceCategoryDescriptions(beneficiaryGroup);
  const issueTypeDescriptions =
    getGrievanceIssueTypeDescriptions(beneficiaryGroup);

  const categoryDescription =
    categoryDescriptions[GRIEVANCE_CATEGORIES_NAMES[values.category]] || '';
  const issueTypeDescription =
    issueTypeDescriptions[GRIEVANCE_ISSUE_TYPES_NAMES[values.issueType]] || '';

  return (
    <Grid container spacing={3}>
      <Grid item xs={6}>
        <Field
          name="category"
          label="Category"
          onChange={(e) => {
            setFieldValue('issueType', null);
            handleChange(e);
          }}
          variant="outlined"
          choices={choicesData.grievanceTicketManualCategoryChoices}
          component={FormikSelectField}
          disabled={redirectedFromRelatedTicket}
          required
        />
      </Grid>
      {showIssueType(values) && (
        <Grid item xs={6}>
          <Field
            name="issueType"
            label="Issue Type"
            variant="outlined"
            choices={
              redirectedFromRelatedTicket
                ? dataChangeIssueTypes
                : issueTypeDict[values.category].subCategories
            }
            component={FormikSelectField}
            required
          />
        </Grid>
      )}
      {values.category && (
        <>
          <DividerLine />
          <Grid item xs={6}>
            <LabelizedField label={t('Category Description')}>
              {categoryDescription}
            </LabelizedField>
          </Grid>
          {issueTypeDescription && (
            <Grid item xs={6}>
              <LabelizedField label={t('Issue Type Description')}>
                {issueTypeDescription}
              </LabelizedField>
            </Grid>
          )}
        </>
      )}
    </Grid>
  );
}
