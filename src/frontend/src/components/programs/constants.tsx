import { ProgramPartnerAccess } from '@generated/graphql';

export const PartnerAccess = {
  [ProgramPartnerAccess.NonePartnersAccess]:
    'None of the Partners should have access',
  [ProgramPartnerAccess.SelectedPartnersAccess]:
    'Only Selected Partners within the business area',
  [ProgramPartnerAccess.AllPartnersAccess]:
    'All Current Partners within the business area',
};

export const partnerAccessChoices = Object.entries(PartnerAccess).map(
  ([value, label]) => ({
    value,
    label,
  }),
);
