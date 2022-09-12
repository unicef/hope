import { GrievancesChoiceDataQuery } from '../../src/__generated__/graphql';

export const fakeGrievancesChoices = {
  grievanceTicketStatusChoices: [
    { name: 'New', value: '1', __typename: 'ChoiceObject' },
    { name: 'Assigned', value: '2', __typename: 'ChoiceObject' },
    { name: 'Closed', value: '6', __typename: 'ChoiceObject' },
    { name: 'For Approval', value: '5', __typename: 'ChoiceObject' },
    { name: 'In Progress', value: '3', __typename: 'ChoiceObject' },
    { name: 'On Hold', value: '4', __typename: 'ChoiceObject' },
  ],
  grievanceTicketCategoryChoices: [
    { name: 'Data Change', value: '2', __typename: 'ChoiceObject' },
    { name: 'Grievance Complaint', value: '4', __typename: 'ChoiceObject' },
    { name: 'Needs Adjudication', value: '8', __typename: 'ChoiceObject' },
    { name: 'Negative Feedback', value: '5', __typename: 'ChoiceObject' },
    { name: 'Payment Verification', value: '1', __typename: 'ChoiceObject' },
    { name: 'Positive Feedback', value: '7', __typename: 'ChoiceObject' },
    { name: 'Referral', value: '6', __typename: 'ChoiceObject' },
    { name: 'Sensitive Grievance', value: '3', __typename: 'ChoiceObject' },
    { name: 'System Flagging', value: '9', __typename: 'ChoiceObject' },
  ],
  grievanceTicketSubCategoryChoices: [
    {
      name: 'Payment Related Complaint',
      value: '1',
      __typename: 'ChoiceObject',
    },
    {
      name: 'FSP Related Complaint',
      value: '2',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Registration Related Complaint',
      value: '3',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Other Complaint',
      value: '4',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Partner Related Complaint',
      value: '5',
      __typename: 'ChoiceObject',
    },
  ],
  grievanceTicketManualCategoryChoices: [
    { name: 'Data Change', value: '2', __typename: 'ChoiceObject' },
    { name: 'Grievance Complaint', value: '4', __typename: 'ChoiceObject' },
    { name: 'Negative Feedback', value: '5', __typename: 'ChoiceObject' },
    { name: 'Positive Feedback', value: '7', __typename: 'ChoiceObject' },
    { name: 'Referral', value: '6', __typename: 'ChoiceObject' },
    { name: 'Sensitive Grievance', value: '3', __typename: 'ChoiceObject' },
  ],
  grievanceTicketIssueTypeChoices: [
    {
      category: '2',
      label: 'Data Change',
      subCategories: [
        { name: 'Add Individual', value: '16', __typename: 'ChoiceObject' },
        {
          name: 'Household Data Update',
          value: '13',
          __typename: 'ChoiceObject',
        },
        {
          name: 'Individual Data Update',
          value: '14',
          __typename: 'ChoiceObject',
        },
        {
          name: 'Withdraw Individual',
          value: '15',
          __typename: 'ChoiceObject',
        },
      ],
      __typename: 'IssueTypesObject',
    },
    {
      category: '3',
      label: 'Sensitive Grievance',
      subCategories: [
        {
          name: 'Bribery, corruption or kickback',
          value: '2',
          __typename: 'ChoiceObject',
        },
        { name: 'Data breach', value: '1', __typename: 'ChoiceObject' },
        {
          name: 'Conflict of interest',
          value: '8',
          __typename: 'ChoiceObject',
        },
        { name: 'Fraud and forgery', value: '3', __typename: 'ChoiceObject' },
        {
          name: 'Fraud involving misuse of programme funds by third party',
          value: '4',
          __typename: 'ChoiceObject',
        },
        { name: 'Gross mismanagement', value: '9', __typename: 'ChoiceObject' },
        {
          name: 'Harassment and abuse of authority',
          value: '5',
          __typename: 'ChoiceObject',
        },
        {
          name: 'Inappropriate staff conduct',
          value: '6',
          __typename: 'ChoiceObject',
        },
        { name: 'Miscellaneous', value: '12', __typename: 'ChoiceObject' },
        { name: 'Personal disputes', value: '10', __typename: 'ChoiceObject' },
        {
          name: 'Sexual harassment and sexual exploitation',
          value: '11',
          __typename: 'ChoiceObject',
        },
        {
          name: 'Unauthorized use, misuse or waste of UNICEF property or funds',
          value: '7',
          __typename: 'ChoiceObject',
        },
      ],
      __typename: 'IssueTypesObject',
    },
  ],
  grievanceTicketUrgencyChoices: [
    {
      name: 'Very urgent',
      value: 1,
    },
    {
      name: 'Urgent',
      value: 2,
    },
    {
      name: 'Not urgent',
      value: 3,
    },
  ],
  grievanceTicketPriorityChoices: [
    {
      name: 'High',
      value: 1,
    },
    {
      name: 'Medium',
      value: 2,
    },
    {
      name: 'Low',
      value: 3,
    },
  ],
} as GrievancesChoiceDataQuery;
