export const PartnerAccess = {
  ['NONE_PARTNERS_ACCESS']: 'None of the Partners should have access',
  ['SELECTED_PARTNERS_ACCESS']:
    'Only Selected Partners within the business area',
  ['ALL_PARTNERS_ACCESS']: 'All Current Partners within the business area',
};

export const partnerAccessChoices = Object.entries(PartnerAccess).map(
  ([value, label]) => ({
    value,
    label,
  }),
);
