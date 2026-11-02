import { describe, expect, it } from 'vitest';
import { getIssueTypeToDisplay } from './createGrievanceUtils';

const issueTypeChoices = [
  {
    category: 7,
    label: 'Negative Feedback',
    subCategories: {
      19: 'FSP Related Complaint',
      20: 'Registration Related Complaint',
    },
  },
  {
    category: 3,
    label: 'Sensitive Grievance',
    subCategories: { 1: 'Data Breach' },
  },
];

describe('getIssueTypeToDisplay', () => {
  it('uses the label from the issue type choices', () => {
    expect(getIssueTypeToDisplay(19, issueTypeChoices)).toBe(
      'FSP Related Complaint',
    );
    expect(getIssueTypeToDisplay(1, issueTypeChoices)).toBe('Data Breach');
  });

  it('falls back to the title-cased name without choices or a match', () => {
    expect(getIssueTypeToDisplay(19)).toBe('Fsp Complaint');
    expect(getIssueTypeToDisplay(20, [])).toBe('Registration Complaint');
  });

  it('returns an empty string without an issue type', () => {
    expect(getIssueTypeToDisplay(null, issueTypeChoices)).toBe('');
  });
});
