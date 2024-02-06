import { Grid } from '@mui/material';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { GrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { useArrayToDict } from '../../../../hooks/useArrayToDict';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import {
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_CATEGORY_DESCRIPTIONS,
  GRIEVANCE_ISSUE_TYPES_NAMES,
  GRIEVANCE_ISSUE_TYPE_DESCRIPTIONS,
} from '../../../../utils/constants';
import { DividerLine } from '../../../core/DividerLine';
import { LabelizedField } from '../../../core/LabelizedField';

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

  const dataChangeIssueTypes = [
    { name: 'Household Data Update', value: '13' },
    { name: 'Individual Data Update', value: '14' },
  ];

  const categoryDescription = GRIEVANCE_CATEGORY_DESCRIPTIONS[
    GRIEVANCE_CATEGORIES_NAMES[values.category]
  ] || '';
  const issueTypeDescription = GRIEVANCE_ISSUE_TYPE_DESCRIPTIONS[
    GRIEVANCE_ISSUE_TYPES_NAMES[values.issueType]
  ] || '';

  return (
    <Grid container spacing={3}>
      <Grid item xs={6}>
        <Field
          name="category"
          label="Category*"
          onChange={(e) => {
            setFieldValue('issueType', null);
            handleChange(e);
          }}
          variant="outlined"
          choices={choicesData.grievanceTicketManualCategoryChoices}
          component={FormikSelectField}
          disabled={redirectedFromRelatedTicket}
        />
      </Grid>
      {showIssueType(values) && (
        <Grid item xs={6}>
          <Field
            name="issueType"
            label="Issue Type*"
            variant="outlined"
            choices={
              redirectedFromRelatedTicket
                ? dataChangeIssueTypes
                : issueTypeDict[values.category].subCategories
            }
            component={FormikSelectField}
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
