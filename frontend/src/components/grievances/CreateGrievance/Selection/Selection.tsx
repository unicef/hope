import { Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useArrayToDict } from '../../../../hooks/useArrayToDict';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { GrievancesChoiceDataQuery } from '../../../../__generated__/graphql';

export interface SelectionProps {
  handleChange: (e: React.ChangeEvent) => void;
  choicesData: GrievancesChoiceDataQuery;
  setFieldValue: (field: string, value, shouldValidate?: boolean) => void;
  showIssueType: (values) => boolean;
  values;
  redirectedFromRelatedTicket: boolean
}

export const Selection = ({
  handleChange,
  choicesData,
  setFieldValue,
  showIssueType,
  values,
  redirectedFromRelatedTicket
}: SelectionProps): React.ReactElement => {
  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  console.log(redirectedFromRelatedTicket)
  const issueTypeChoices = redirectedFromRelatedTicket ?
      issueTypeDict["2"].subCategories.filter(
          (subCategory) =>
              subCategory.name === "Household Data Update" ||
              subCategory.name === "Individual Data Update"
      ) : issueTypeDict[values.category].subCategories

  return (
    <Grid container spacing={3}>
      <Grid item xs={6}>
        <Field
          name='category'
          label='Category*'
          onChange={(e) => {
            setFieldValue('issueType', null);
            handleChange(e);
          }}
          variant='outlined'
          choices={choicesData.grievanceTicketManualCategoryChoices}
          component={FormikSelectField}
          disabled={redirectedFromRelatedTicket}
        />
      </Grid>
      {showIssueType(values) && (
        <Grid item xs={6}>
          <Field
            name='issueType'
            label='Issue Type*'
            variant='outlined'
            choices={issueTypeChoices}
            component={FormikSelectField}
          />
        </Grid>
      )}
    </Grid>
  );
};
