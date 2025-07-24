/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlankEnum } from './BlankEnum';
import type { CollectTypeEnum } from './CollectTypeEnum';
import type { ConsentSharingEnum } from './ConsentSharingEnum';
import type { CountryEnum } from './CountryEnum';
import type { CountryOriginEnum } from './CountryOriginEnum';
import type { CurrencyEnum } from './CurrencyEnum';
import type { Individual } from './Individual';
import type { OrgEnumeratorEnum } from './OrgEnumeratorEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
import type { RegistrationMethodEnum } from './RegistrationMethodEnum';
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
export type Household = {
  first_registration_date?: string;
  last_registration_date?: string;
  members: Array<Individual>;
  country: CountryEnum;
  country_origin?: CountryOriginEnum;
  size?: number | null;
  rdi_merge_status?: RdiMergeStatusEnum;
  is_original?: boolean;
  readonly created_at: string;
  readonly updated_at: string;
  is_removed?: boolean;
  removed_date?: string | null;
  last_sync_at?: string | null;
  internal_data?: any;
  withdrawn?: boolean;
  withdrawn_date?: string | null;
  consent_sign?: string;
  consent?: boolean | null;
  consent_sharing?: ConsentSharingEnum | BlankEnum;
  residence_status?: ResidenceStatusEnum | BlankEnum;
  address?: string;
  zip_code?: string | null;
  female_age_group_0_5_count?: number | null;
  female_age_group_6_11_count?: number | null;
  female_age_group_12_17_count?: number | null;
  female_age_group_18_59_count?: number | null;
  female_age_group_60_count?: number | null;
  pregnant_count?: number | null;
  male_age_group_0_5_count?: number | null;
  male_age_group_6_11_count?: number | null;
  male_age_group_12_17_count?: number | null;
  male_age_group_18_59_count?: number | null;
  male_age_group_60_count?: number | null;
  female_age_group_0_5_disabled_count?: number | null;
  female_age_group_6_11_disabled_count?: number | null;
  female_age_group_12_17_disabled_count?: number | null;
  female_age_group_18_59_disabled_count?: number | null;
  female_age_group_60_disabled_count?: number | null;
  male_age_group_0_5_disabled_count?: number | null;
  male_age_group_6_11_disabled_count?: number | null;
  male_age_group_12_17_disabled_count?: number | null;
  male_age_group_18_59_disabled_count?: number | null;
  male_age_group_60_disabled_count?: number | null;
  children_count?: number | null;
  maleChildrenCount?: number | null;
  femaleChildrenCount?: number | null;
  children_disabled_count?: number | null;
  male_children_disabled_count?: number | null;
  female_children_disabled_count?: number | null;
  returnee?: boolean | null;
  flex_fields?: any;
  fchild_hoh?: boolean | null;
  child_hoh?: boolean | null;
  start?: string | null;
  deviceid?: string;
  name_enumerator?: string;
  org_enumerator?: OrgEnumeratorEnum | BlankEnum;
  org_name_enumerator?: string;
  village?: string;
  registration_method?: RegistrationMethodEnum | BlankEnum;
  currency?: CurrencyEnum | BlankEnum;
  unhcr_id?: string;
  registration_id?: string | null;
  program_registration_id?: string | null;
  total_cash_received_usd?: string | null;
  total_cash_received?: string | null;
  family_id?: string | null;
  origin_unicef_id?: string | null;
  collect_type?: CollectTypeEnum;
  enumerator_rec_id?: number | null;
  flex_registrations_record_id?: number | null;
  household_collection?: number | null;
  admin_area?: string | null;
  admin1?: string | null;
  admin2?: string | null;
  admin3?: string | null;
  admin4?: string | null;
  storage_obj?: number | null;
  /**
   * If this household was copied from another household, this field will contain the household it was copied from.
   */
  copied_from?: string | null;
  /**
   * This is only used to track collector (primary or secondary) of a household.
   * They may still be a HOH of this household or any other household.
   * Through model will contain the role (ROLE_CHOICE) they are connected with on.
   */
  readonly representatives: Array<string>;
  programs?: Array<string>;
};
