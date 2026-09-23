import camelCase from 'lodash/camelCase';

/**
 * Reading data change ticket details.
 *
 * The REST client camelizes every response (see `deepCamelize` in utils), but
 * `household_data` is listed in its `notCamelizedKeys`: the key becomes
 * `householdData` while everything inside it stays snake_case (`flex_fields`,
 * `previous_value`, `approve_status`). `individual_data` is camelized all the
 * way down, except for flex field names ending in `_i_f` / `_h_f`, which are
 * left alone so they still match the attribute they came from.
 *
 * Every reader of a data change ticket has to account for that asymmetry, so it
 * lives here instead of being repeated at each call site.
 */

export interface TicketFieldChange {
  value?: any;
  previousValue?: any;
  approveStatus?: boolean;
}

export const getTicketData = (
  ticketDetails: any,
  isIndividual?: boolean,
): any =>
  (isIndividual
    ? ticketDetails?.individualData
    : ticketDetails?.householdData) || {};

export const getTicketFlexFields = (
  ticketDetails: any,
  isIndividual?: boolean,
): Record<string, any> => {
  const data = getTicketData(ticketDetails, isIndividual);
  return (isIndividual ? data.flexFields : data.flex_fields) || {};
};

/** The key a core field is stored under in this ticket's data. */
export const getTicketFieldKey = (
  fieldName: string,
  isIndividual?: boolean,
): string => (isIndividual ? camelCase(fieldName) : fieldName);

/**
 * The requested change for a single field, flex or core. Core IMAGE fields
 * (`photo`, `consent_sign`) sit next to `flex_fields`, not inside them.
 */
export const getTicketFieldChange = (
  ticketDetails: any,
  fieldName: string,
  isIndividual?: boolean,
): any => {
  const data = getTicketData(ticketDetails, isIndividual);
  const flexFields = getTicketFlexFields(ticketDetails, isIndividual);
  const key = getTicketFieldKey(fieldName, isIndividual);
  return flexFields[fieldName] ?? flexFields[key] ?? data[key];
};

/** A change read in the same shape no matter which side of the ticket it is on. */
export const normalizeTicketFieldChange = (
  change: any,
  isIndividual?: boolean,
): TicketFieldChange => ({
  value: change?.value,
  previousValue: isIndividual ? change?.previousValue : change?.previous_value,
  approveStatus: isIndividual ? change?.approveStatus : change?.approve_status,
});

/** True for a value that is a requested change, on either side of the ticket. */
export const isTicketFieldChange = (value: any): boolean =>
  typeof value === 'object' &&
  value !== null &&
  (typeof value.approve_status === 'boolean' ||
    typeof value.approveStatus === 'boolean');

export const isApprovedTicketFieldChange = (value: any): boolean =>
  isTicketFieldChange(value) &&
  (value.approve_status === true || value.approveStatus === true);

// grouped changes are counted through the list holding them, not twice
const NOT_SINGLE_CHANGES = [
  'previous_documents',
  'previousDocuments',
  'previous_identities',
  'previousIdentities',
  'previous_payment_channels',
  'previousPaymentChannels',
  'flex_fields',
  'flexFields',
];

/** Approved against still unapproved changes requested by a data change ticket. */
export const countTicketChanges = (
  ticketDetails: any,
): { approved: number; notApproved: number } => {
  const allChanges = {
    ...getTicketData(ticketDetails),
    ...getTicketData(ticketDetails, true),
    ...getTicketFlexFields(ticketDetails),
    ...getTicketFlexFields(ticketDetails, true),
  };
  let approved = 0;
  let notApproved = 0;
  Object.entries(allChanges)
    .filter(([key]) => !NOT_SINGLE_CHANGES.includes(key))
    .flatMap(([, value]) => (Array.isArray(value) ? value.flat() : [value]))
    .filter(isTicketFieldChange)
    .forEach((change) => {
      if (isApprovedTicketFieldChange(change)) {
        approved += 1;
      } else {
        notApproved += 1;
      }
    });

  return { approved, notApproved };
};
