import { ProgramPartnerAccess } from '@generated/graphql';

export const PartnerAccess = {
  [ProgramPartnerAccess.NonePartnersAccess]:
    'None of the partners should have access',
  [ProgramPartnerAccess.SelectedPartnersAccess]:
    'Only selected partners within the business area',
  [ProgramPartnerAccess.AllPartnersAccess]:
    'All partners within the business area',
};

export const partnerAccessChoices = Object.entries(PartnerAccess).map(
  ([value, label]) => ({
    value,
    label,
  }),
);

console.log(partnerAccessChoices);
